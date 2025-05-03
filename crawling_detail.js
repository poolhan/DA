
// const puppeteer = require("puppeteer");

// (async () => {
//   const url = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=362922298";
//   const browser = await puppeteer.launch({ headless: true });
//   const page = await browser.newPage();

//   // 브라우저 콘솔 로그 출력
//   page.on("console", (msg) => {
//     for (let i = 0; i < msg.args().length; ++i) {
//       msg.args()[i].jsonValue().then((val) => {
//         console.log("🔥 브라우저 로그:", val);
//       });
//     }
//   });

//   await page.goto(url, { waitUntil: "networkidle2" });

//   // 책소개 더보기 클릭
//   const introMore = await page.$("#PreviewMore1");
//   if (introMore) {
//     await introMore.click();
//     await page.waitForTimeout(1000);
//   }

//   // 책속에서 큰 더보기 클릭
//   const excerptMore = await page.$("#Underline3_more a");
//   if (excerptMore) {
//     await excerptMore.click();
//     await page.waitForTimeout(1500);
//   }

//   // 책속에서 내부 더보기 클릭 (문단 펼치기)
//   const innerMoreButtons = await page.$$('a[onclick*="toggle_contents"]');
//   for (const btn of innerMoreButtons) {
//     try {
//       await btn.click();
//       await page.waitForTimeout(100);
//     } catch (e) {}
//   }

//   const data = await page.evaluate(() => {
//     const getText = (selector) => {
//       const el = document.querySelector(selector);
//       return el ? el.textContent.trim() : null;
//     };

//     const extractCountFromLink = (hrefPart) => {
//       const el = document.querySelector(`a[href*='${hrefPart}']`);
//       if (!el) return null;
//       const match = el.textContent.match(/\((\d+)\)/);
//       return match ? parseInt(match[1]) : null;
//     };

//     const lis = Array.from(document.querySelectorAll(".conts_info_list1 li")).map(li => li.textContent.trim());

//     const pageCount = lis.find(t => t.includes("쪽"))?.replace("쪽", "").trim() || null;
//     const size = lis.find(t => t.includes("mm")) || null;
//     const weight = lis.find(t => t.includes("g")) || null;
//     const isbnLine = lis.find(t => t.includes("ISBN"));
//     const isbn = isbnLine ? isbnLine.replace("ISBN :", "").trim() : null;

//     const rating = getText(".Ere_sub_pink.Ere_fs16.Ere_str");
//     const shortReviewCount = extractCountFromLink("_CommentReview");
//     const fullReviewCount = extractCountFromLink("_MyReview");

//     const records = (() => {
//       const el = document.querySelector("#wa_product_top1_wa_Top_Ranking_pnlRanking");
//       return el ? el.innerText.replace(/\s+/g, " ").trim() : null;
//     })();

//     const publishDate = (() => {
//       const el = Array.from(document.querySelectorAll("li"))
//         .map(li => li.textContent)
//         .find(t => /\d{4}-\d{2}-\d{2}/.test(t));
//       return el?.match(/\d{4}-\d{2}-\d{2}/)?.[0] || null;
//     })();

//     const bookDescription = (() => {
//       const contents = Array.from(document.querySelectorAll(".Ere_prod_mconts_R"))
//         .map(el => el.innerText.trim())
//         .filter(text => text.length > 50);
//       if (contents.length === 0) return null;
//       return contents.reduce((a, b) => (a.length > b.length ? a : b));
//     })();

//     const bookExcerpt = (() => {
//       const excerpts = [...document.querySelectorAll(".Rconts2")]
//         .map(div => div.innerText.trim())
//         .filter(t => t.length > 0);
//       return excerpts.length > 0 ? excerpts.join("\n\n") : null;
//     })();

//     return {
//       title: getText("#Ere_prod_allwrap h2"),
//       author: getText("a.Ere_sub2_title[href*='AuthorSearch']"),
//       publisher: getText("a.Ere_sub2_title[href*='PublisherSearch']"),
//       price: getText(".Ritem"),

//       publishDate,
//       pageCount,
//       size,
//       weight,
//       isbn,

//       rating,
//       shortReviewCount,
//       fullReviewCount,
//       records,
//       bookDescription,
//       bookExcerpt
//     };
//   });

//   console.log(data);
//   await browser.close();
// })();
const puppeteer = require("puppeteer");

(async () => {
  const url = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=362922298";
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // 브라우저 콘솔 로그 출력
  page.on("console", (msg) => {
    for (let i = 0; i < msg.args().length; ++i) {
      msg.args()[i].jsonValue().then((val) => {
        console.log("🔥 브라우저 로그:", val);
      });
    }
  });

  await page.goto(url, { waitUntil: "networkidle2" });

  // 책소개 더보기 클릭
  const introMore = await page.$("#PreviewMore1");
  if (introMore) {
    await introMore.click();
    await page.waitForTimeout(1000);
  }

  // ✅ 책속에서 큰 더보기 클릭
  const excerptMore = await page.$("#Underline3_more a");
  if (excerptMore) {
    await excerptMore.click();
    await page.waitForTimeout(1500);
  }

  // ✅ 책속에서 내부 문단 더보기 펼치기 (.Ere_sub_gray8.Ere_fs13 클릭)
  const innerMoreButtons = await page.$$('a.Ere_sub_gray8.Ere_fs13');
  for (const btn of innerMoreButtons) {
    try {
      await btn.click();
      await page.waitForTimeout(100);
    } catch (e) {}
  }

  const data = await page.evaluate(() => {
    const getText = (selector) => {
      const el = document.querySelector(selector);
      return el ? el.textContent.trim() : null;
    };

    const extractCountFromLink = (hrefPart) => {
      const el = document.querySelector(`a[href*='${hrefPart}']`);
      if (!el) return null;
      const match = el.textContent.match(/\((\d+)\)/);
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
      return el ? el.innerText.replace(/\s+/g, " ").trim() : null;
    })();

    const publishDate = (() => {
      const el = Array.from(document.querySelectorAll("li"))
        .map(li => li.textContent)
        .find(t => /\d{4}-\d{2}-\d{2}/.test(t));
      return el?.match(/\d{4}-\d{2}-\d{2}/)?.[0] || null;
    })();

    const bookDescription = (() => {
      const contents = Array.from(document.querySelectorAll(".Ere_prod_mconts_R"))
        .map(el => el.innerText.trim())
        .filter(text => text.length > 50);
      if (contents.length === 0) return null;
      return contents.reduce((a, b) => (a.length > b.length ? a : b));
    })();

    // ✅ 책속에서 추출 (.Rconts2 기준)
    const bookExcerpt = (() => {
      const excerpts = [...document.querySelectorAll(".Rconts2")]
        .map(div => div.innerText.trim())
        .filter(t => t.length > 0);
      return excerpts.length > 0 ? excerpts.join("\n\n") : null;
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
      bookExcerpt
    };
  });

  console.log(data);
  await browser.close();
})();
