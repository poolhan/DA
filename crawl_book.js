

const mysql = require("mysql2/promise");
const puppeteer = require("puppeteer");

const MAX_RETRY = 2;
const TIMEOUT = 60000;
const CONCURRENCY = 3;
const MAX_CHUNK_BEFORE_RESTART = 100;
const MAX_AUTHOR_URL_LENGTH = 800;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function applyStealth(page) {
  // User-Agent 및 navigator 조작
  await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36");
  await page.setExtraHTTPHeaders({ "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7" });

  await page.evaluateOnNewDocument(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false,
    });
  });
}

async function extractAndInsert(urls, insertTable, db) {
  const chunks = [];
  for (let i = 0; i < urls.length; i += CONCURRENCY) {
    chunks.push(urls.slice(i, i + CONCURRENCY));
  }

  const failures = [];
  let browser = await puppeteer.launch({ headless: false, defaultViewport: null });

  for (let chunkIndex = 0; chunkIndex < chunks.length; chunkIndex++) {
    if (chunkIndex > 0 && chunkIndex % MAX_CHUNK_BEFORE_RESTART === 0) {
      console.log("♻️ 브라우저 재시작 중...");
      await browser.close();
      browser = await puppeteer.launch({ headless: false, defaultViewport: null });
    }

    const chunk = chunks[chunkIndex];

    await Promise.all(chunk.map(async (item, index) => {
      const url = item.urls;
      const page = await browser.newPage();
      page.setDefaultNavigationTimeout(TIMEOUT);

      try {
        await applyStealth(page); // ✅ 탐지 우회 설정

        let success = false;
        for (let attempt = 0; attempt <= MAX_RETRY; attempt++) {
          try {
            await page.goto(url, { waitUntil: "networkidle2" });
            success = true;
            break;
          } catch (err) {
            if (attempt < MAX_RETRY) {
              console.warn(`🔁 재시도 (${attempt + 1})회: ${url}`);
              await sleep(1000 + Math.random() * 1000); // ✅ 랜덤 지연
            } else {
              throw err;
            }
          }
        }

        if (!success) return;

        const result = await page.evaluate(() => {
          let isbn = null;
          document.querySelectorAll("div.conts_info_list1 li").forEach(li => {
            if (li.innerText.includes("ISBN")) {
              isbn = li.innerText.replace("ISBN :", "").trim().split(" ")[0];
            }
          });

          const authorElements = Array.from(document.querySelectorAll("a[href*='AuthorSearch']"));
          const authorNames = authorElements.map(a => a.textContent.trim()).join("/") || null;
          const authorLinks = authorElements.map(a => a.href).join("/") || null;

          return { isbn, authorNames, authorLinks };
        });

        let trimmedAuthorLinks = result.authorLinks;
        if (trimmedAuthorLinks && trimmedAuthorLinks.length > MAX_AUTHOR_URL_LENGTH) {
          console.warn(`⚠️ author_url 길이 초과. 자름: ${url}`);
          trimmedAuthorLinks = trimmedAuthorLinks.slice(0, MAX_AUTHOR_URL_LENGTH);
        }

        await db.execute(
          `INSERT INTO ${insertTable} (isbn, author, author_url, book_url) VALUES (?, ?, ?, ?)`,
          [result.isbn, result.authorNames, trimmedAuthorLinks, url]
        );

        console.log(`✅ (${chunkIndex * CONCURRENCY + index + 1}/${urls.length}) INSERT 성공: ${url}`);
        await sleep(500 + Math.random() * 1500); // ✅ 인간처럼 랜덤한 지연 추가
      } catch (err) {
        console.error(`❌ (${chunkIndex * CONCURRENCY + index + 1}/${urls.length}) 실패: ${url}`, err.message);
        failures.push(url);
      } finally {
        await page.close();
      }
    }));
  }

  await browser.close();

  if (failures.length > 0) {
    console.warn(`⚠️ 총 ${failures.length}건 실패. 실패 URL 목록을 기록합니다.`);
    require("fs").writeFileSync("failures.txt", failures.join("\n"));
  }
}

(async () => {
  const db = await mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'your_database_name',
    waitForConnections: true,
    connectionLimit: 5,
  });

  const [bestsellerUrls] = await db.execute("SELECT * FROM best_urls");
  const [bookUrls] = await db.execute("SELECT * FROM book_url");

  console.log("📚 베스트셀러 URL 처리 중...");
  await extractAndInsert(bestsellerUrls, "bestsellers", db);

  console.log("📘 일반도서 URL 처리 중...");
  await extractAndInsert(bookUrls, "book", db);

  await db.end();
})();
