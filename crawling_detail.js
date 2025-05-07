
const puppeteer = require("puppeteer");
const { execSync } = require("child_process");
const path = require("path");
const mysql = require("mysql2/promise");
const readline = require("readline");


const INSERT_TABLE = "Bestraw"; // INSERT할 테이블명
const PYTHON_EXE = "py_crawl_excerpt.exe"; // 실행할 Python EXE 이름

function waitAndExit(message) {
  console.error(message || "❌ 오류가 발생했습니다.");
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.question("\n🔚 Enter 키를 누르면 종료됩니다...", () => {
    rl.close();
    process.exit(1);
  });
}

process.on("uncaughtException", (err) => waitAndExit("❗ Uncaught Exception: " + err.message));
process.on("unhandledRejection", (reason) => waitAndExit("❗ Unhandled Rejection: " + reason));

async function extractOne(url, exeDir) {
  let browser;
  let data = {};
  let bookExcerpt = null;
  let errorMessage = null;

  try {
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "networkidle2" });

    // ✅ 책소개 스크롤 유도
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight / 2);
    });
    await new Promise(resolve => setTimeout(resolve, 1000));

    const introMore = await page.$("#PreviewMore1");
    if (introMore) {
      await introMore.click();
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    const result = await page.evaluate(new Function("dummyUrl", `
      const _ = dummyUrl;

      const getText = (selector) => {
        const el = document.querySelector(selector);
        return el ? el.textContent.trim() : null;
      };

      const extractCountFromLink = (hrefPart) => {
        const el = document.querySelector(\`a[href*="\${hrefPart}"]\`);
        if (!el) return null;
        const match = el.textContent.match(/\\((\\d+)\\)/);
        return match ? parseInt(match[1]) : null;
      };

      const lis = Array.from(document.querySelectorAll(".conts_info_list1 li")).map(li => li.textContent.trim());
      const pageCount = lis.find(t => t.includes("쪽"))?.replace("쪽", "").trim() || null;
      const size = lis.find(t => t.includes("mm")) || null;
      const weight = lis.find(t => t.includes("g")) || null;
      const isbnLine = lis.find(t => t.includes("ISBN"));
      const isbn = isbnLine ? isbnLine.replace("ISBN :", "").trim() : null;

      const rating = getText(".Ere_sub_pink.Ere_fs16.Ere_str");
      const shortReviewCount = extractCountFromLink("_CommentReview");
      const fullReviewCount = extractCountFromLink("_MyReview");

      const records = (() => {
        const el = document.querySelector("#wa_product_top1_wa_Top_Ranking_pnlRanking");
        return el ? el.innerText.replace(/\\s+/g, " ").trim() : null;
      })();

      const publishDate = (() => {
        const el = Array.from(document.querySelectorAll("li"))
          .map(li => li.textContent)
          .find(t => /\\d{4}-\\d{2}-\\d{2}/.test(t));
        return el?.match(/\\d{4}-\\d{2}-\\d{2}/)?.[0] || null;
      })();


      return {
        title: getText(".Ere_bo_title"),
        author: getText("a.Ere_sub2_title[href*='AuthorSearch']"),
        publisher: getText("a.Ere_sub2_title[href*='PublisherSearch']"),
        price: getText(".Ritem"),

        publishDate,
        pageCount,
        size,
        weight,
        isbn,

        rating,
        shortReviewCount,
        fullReviewCount,
        records,
      };
    `), url);

    

    data = result;
    await browser.close();
  } catch (e) {
    if (browser) await browser.close();
    console.error(`❌ Puppeteer 오류 (${url}) →`, e.message);
    return null;
  }

  try {
    const exeDir = path.dirname(process.execPath); // ← 현재 실행파일 기준 경로
    const pyExePath = path.join(exeDir, PYTHON_EXE);
    const result = execSync(`"${pyExePath}" "${url}"`, { encoding: "utf-8" });
    bookExcerpt = result.trim();
  } catch (e) {
    errorMessage = e.message;
  }

  return {
    ...data,
    bookExcerpt,
    book_url: url
  };
}

(async () => {
  const exeDir = path.dirname(process.execPath);

  const db = await mysql.createPool({
    host: '',
    port: ,  
    user: '',
    password: '',
    database: '',
    waitForConnections: true,
    connectionLimit: 5,
  });

  const [rows] = await db.execute(
    `SELECT book_url FROM best_selected LIMIT 907, 93`
  );

  for (let i = 0; i < rows.length; i++) {
    const url = rows[i].book_url;
    console.log(`🔎 (${i + 1}/${rows.length}) 수집 중: ${url}`);
    const finalData = await extractOne(url, exeDir);
    if (!finalData) continue;

    try {
      await db.execute(`
        INSERT INTO ${INSERT_TABLE} (
          isbn, title, author, publisher, price, publishDate,
          pageCount, size, weight, rating, shortReviewCount,
          fullReviewCount, records, bookDescription, bookExcerpt, book_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `, [
        finalData.isbn,
        finalData.title,
        finalData.author,
        finalData.publisher,         // ✅ 오타 수정
        finalData.price,
        finalData.publishDate,
        finalData.pageCount,
        finalData.size,
        finalData.weight,
        finalData.rating,
        finalData.shortReviewCount,
        finalData.fullReviewCount,
        finalData.records,
        finalData.bookDescription,
        finalData.bookExcerpt,      // ✅ 컬럼명 수정
        finalData.book_url
      ]);
      console.log("✅ INSERT 성공\n");
    } catch (e) {
      console.error("❌ DB INSERT 실패 →", e.message);
    }
  }

  await db.end();

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.question("\n🔚 모든 작업 완료. Enter 키를 누르면 종료됩니다...", () => rl.close());
})();
