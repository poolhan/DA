
// const puppeteer = require("puppeteer");
// const { execSync } = require("child_process");
// const fs = require("fs");
// const path = require("path");
// const readline = require("readline");

// function waitAndExit(message) {
//   console.error(message || "❌ 오류가 발생했습니다.");
//   const rl = readline.createInterface({
//     input: process.stdin,
//     output: process.stdout
//   });
//   rl.question("\n🔚 Enter 키를 누르면 종료됩니다...", () => {
//     rl.close();
//     process.exit(1);
//   });
// }

// process.on("uncaughtException", (err) => {
//   waitAndExit("❗ Uncaught Exception: " + err.message);
// });
// process.on("unhandledRejection", (reason) => {
//   waitAndExit("❗ Unhandled Rejection: " + reason);
// });

// (async () => {
//   const url = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=362922298";
//   const exeDir = path.dirname(process.execPath); // pkg로 만든 exe 위치
//   let browser;
//   let data = {};
//   let bookExcerpt = null;
//   let errorMessage = null;

//   try {
//     browser = await puppeteer.launch({ headless: true });
//     const page = await browser.newPage();
//     await page.goto(url, { waitUntil: "networkidle2" });

//     const introMore = await page.$("#PreviewMore1");
//     if (introMore) {
//       await introMore.click();
//       await page.waitForTimeout(1000);
//     }

//     const result = await page.evaluate(new Function("dummyUrl", `
//       const _ = dummyUrl;

//       const titleEl = document.querySelector(".Ere_bo_title");
//       const authorEl = document.querySelector("a.Ere_sub2_title[href*='AuthorSearch']");
//       const publisherEl = document.querySelector("a.Ere_sub2_title[href*='PublisherSearch']");
//       const priceEl = document.querySelector(".Ritem");

//       let pageCount = null;
//       let size = null;
//       let weight = null;
//       let isbn = null;

//       const lis = Array.from(document.querySelectorAll(".conts_info_list1 li"));
//       for (let i = 0; i < lis.length; i++) {
//         const text = lis[i].textContent.trim();
//         if (text.includes("쪽")) {
//           pageCount = text.replace("쪽", "").trim();
//         } else if (text.includes("mm")) {
//           size = text;
//         } else if (text.includes("g")) {
//           weight = text;
//         } else if (text.includes("ISBN")) {
//           isbn = text.replace("ISBN :", "").trim();
//         }
//       }

//       return {
//         title: titleEl ? titleEl.textContent.trim() : null,
//         author: authorEl ? authorEl.textContent.trim() : null,
//         publisher: publisherEl ? publisherEl.textContent.trim() : null,
//         price: priceEl ? priceEl.textContent.trim() : null,
//         pageCount,
//         size,
//         weight,
//         isbn
//       };
//     `), url);

//     data = result;

//     await browser.close();
//   } catch (e) {
//     if (browser) await browser.close();
//     waitAndExit("❌ Puppeteer 실행 중 오류:\n" + e.message);
//     return;
//   }

//   try {
//     const pyExePath = path.join(exeDir, "py_crawl_excerpt.exe");
//     const result = execSync(`"${pyExePath}" "${url}"`, { encoding: "utf-8" });
//     bookExcerpt = result.trim();
//     console.log("📘 책속에서 추출 성공\n", bookExcerpt.slice(0, 300));
//   } catch (e) {
//     errorMessage = "❌ Python 실행 실패:\n" + e.message;
//     console.error(errorMessage);
//   }

//   const finalData = {
//     ...data,
//     bookExcerpt,
//     error: errorMessage,
//   };

//   try {
//     const outputPath = path.join(exeDir, "result_output.txt");
//     fs.writeFileSync(outputPath, JSON.stringify(finalData, null, 2), "utf-8");
//     console.log("✅ 저장 완료 → result_output.txt");
//   } catch (e) {
//     waitAndExit("❌ 파일 저장 실패:\n" + e.message);
//     return;
//   }

//   const rl = readline.createInterface({
//     input: process.stdin,
//     output: process.stdout
//   });
//   rl.question("\n🔚 모든 작업 완료. Enter 키를 누르면 종료됩니다...", () => {
//     rl.close();
//   });
// })();
// const puppeteer = require("puppeteer");
// const { execSync } = require("child_process");
// const path = require("path");
// const mysql = require("mysql2/promise");

// const BATCH_SIZE = 1000; // 가져올 URL 수
// const OFFSET = 0; // 시작 위치
// const SELECT_TABLE = "best_selected"; // URL이 들어있는 테이블명
// const INSERT_TABLE = "Bestraw"; // INSERT할 테이블명
// const PYTHON_EXE = "py_crawl_excerpt.exe"; // 실행할 Python EXE 이름

// async function extractOne(url, exeDir) {
//   let browser;
//   let data = {};
//   let bookExcerpt = null;

//   try {
//     browser = await puppeteer.launch({ headless: true });
//     const page = await browser.newPage();
//     await page.goto(url, { waitUntil: "networkidle2" });

//     const introMore = await page.$("#PreviewMore1");
//     if (introMore) {
//       await introMore.click();
//       await page.waitForTimeout(1000);
//     }

//     const result = await page.evaluate(new Function("dummyUrl", `
//       const _ = dummyUrl;

//       const getText = (selector) => {
//         const el = document.querySelector(selector);
//         return el ? el.textContent.trim() : null;
//       };

//       const extractCountFromLink = (hrefPart) => {
//         const el = document.querySelector(\`a[href*="\${hrefPart}"]\`);
//         if (!el) return null;
//         const match = el.textContent.match(/\\((\\d+)\\)/);
//         return match ? parseInt(match[1]) : null;
//       };

//       const lis = Array.from(document.querySelectorAll(".conts_info_list1 li")).map(li => li.textContent.trim());
//       const pageCount = lis.find(t => t.includes("쪽"))?.replace("쪽", "").trim() || null;
//       const size = lis.find(t => t.includes("mm")) || null;
//       const weight = lis.find(t => t.includes("g")) || null;
//       const isbnLine = lis.find(t => t.includes("ISBN"));
//       const isbn = isbnLine ? isbnLine.replace("ISBN :", "").trim() : null;

//       const rating = getText(".Ere_sub_pink.Ere_fs16.Ere_str");
//       const shortReviewCount = extractCountFromLink("_CommentReview");
//       const fullReviewCount = extractCountFromLink("_MyReview");

//       const records = (() => {
//         const el = document.querySelector("#wa_product_top1_wa_Top_Ranking_pnlRanking");
//         return el ? el.innerText.replace(/\\s+/g, " ").trim() : null;
//       })();

//       const publishDate = (() => {
//         const el = Array.from(document.querySelectorAll("li"))
//           .map(li => li.textContent)
//           .find(t => /\\d{4}-\\d{2}-\\d{2}/.test(t));
//         return el?.match(/\\d{4}-\\d{2}-\\d{2}/)?.[0] || null;
//       })();

//       const bookDescription = (() => {
//         const contents = Array.from(document.querySelectorAll(".Ere_prod_mconts_R"))
//           .map(el => el.innerText.trim())
//           .filter(text => text.length > 50);
//         if (contents.length === 0) return null;
//         return contents.reduce((a, b) => (a.length > b.length ? a : b));
//       })();

//       return {
//         title: getText(".Ere_bo_title"),
//         author: getText("a.Ere_sub2_title[href*='AuthorSearch']"),
//         publisher: getText("a.Ere_sub2_title[href*='PublisherSearch']"),
//         price: getText(".Ritem"),
//         publishDate,
//         pageCount,
//         size,
//         weight,
//         isbn,
//         rating,
//         shortReviewCount,
//         fullReviewCount,
//         records,
//         bookDescription,
//       };
//     `), url);

//     data = result;
//     await browser.close();
//   } catch (e) {
//     if (browser) await browser.close();
//     console.error(`❌ Puppeteer 오류: ${e.message}`);
//     return null;
//   }

//   try {
//     const pyExePath = path.join(__dirname, PYTHON_EXE);
//     const result = execSync(`"${pyExePath}" "${url}"`, { encoding: "utf-8" });
//     bookExcerpt = result.trim();
//   } catch (e) {
//     bookExcerpt = null;
//   }

//   return {
//     ...data,
//     bookExcerpt,
//     book_url: url
//   };
// }

// (async () => {
//   const exeDir = __dirname;
//   const db = await mysql.createPool({
//     host: '134.185.117.240',
//     port: 3306,
//     user: 'db5',
//     password: 'db3',
//     database: 'DA',
//     waitForConnections: true,
//     connectionLimit: 5,
//   });

//   const [rows] = await db.execute(
//     `SELECT book_url FROM ${SELECT_TABLE} LIMIT ?, ?`,
//     [OFFSET, BATCH_SIZE]
//   );

//   for (let i = 0; i < rows.length; i++) {
//     const url = rows[i].book_url;
//     console.log(`📘 (${i + 1}/${rows.length}) 처리 중: ${url}`);

//     const finalData = await extractOne(url, exeDir);
//     if (!finalData) continue;

//     try {
//       await db.execute(`
//         INSERT INTO ${INSERT_TABLE} (
//           isbn, title, author, publisher, price, publishDate,
//           pageCount, size, weight, rating, shortReviewCount,
//           fullReviewCount, records, bookDescription, bookExcerpt, book_url
//         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
//       `, [
//         finalData.isbn,
//         finalData.title,
//         finalData.author,
//         finalData.publisher,
//         finalData.price,
//         finalData.publishDate,
//         finalData.pageCount,
//         finalData.size,
//         finalData.weight,
//         finalData.rating,
//         finalData.shortReviewCount,
//         finalData.fullReviewCount,
//         finalData.records,
//         finalData.bookDescription,
//         finalData.bookExcerpt,
//         finalData.book_url
//       ]);

//       console.log("✅ INSERT 성공");
//     } catch (err) {
//       console.error("❌ INSERT 실패:", err.message);
//     }
//   }

//   await db.end();
// })();
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

    const introMore = await page.$("#PreviewMore1");
    if (introMore) {
      await introMore.click();
      await page.waitForTimeout(1000);
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
    
      const bookDescription = (() => {
        const contents = Array.from(document.querySelectorAll(".Ere_prod_mconts_R"))
          .map(el => el.innerText.trim())
          .filter(text => text.length > 50);
        if (contents.length === 0) return null;
        return contents.reduce((a, b) => (a.length > b.length ? a : b));
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
        bookDescription,
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
    `SELECT book_url FROM best_selected LIMIT 0, 1000`
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
