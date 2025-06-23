/*
* @description
 * 1. npm 설치 (node도 자동으로 설치됨)
 * 2. 로컬서버를 실행
 * 3. 알라딘 주소에 axios 라이브러리를 사용해서 get 요청 보내서 목록 불러옴. (응답: 링크 목록)
 *  a. query인 page를 동적으로 바꿔가면서 배열에 1000개 데이터를 저장할 수 있도록 함.
 * 4. for loop을 돌려서 각 링크마다 get 요청 보내서 상세 정보 불러오고, 필요한 필드를 DB에 저장.*/
import mysql from 'mysql2/promise';
import axios from 'axios';
import fs from 'fs';


// ✅ DB 연결
const db = await mysql.createConnection({
  host: '',
  port: ,  
  user: '',
  password: '',
  database: '',
});


// 베스트셀러 URL 기본 구조
const baseURL = "https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID=50993";
//bestseller들 페이지 링크리스트트
let urls = [];

// 연도 및 월 범위 정의
const validMonths = {
    2024: [4, 5, 6, 7, 8, 9, 10, 11, 12],
    2025: [1, 2, 3, 4],
};

for (let year of [2024, 2025]) {
    for (let month of validMonths[year]) {
        for (let week = 1; week <= 5; week++) {
            for (let page = 1; page <= 20; page++) {
                const url = `${baseURL}&Year=${year}&Month=${month}&Week=${week}&page=${page}&cnt=1000&SortOrder=1`;
                urls.push(url);
            }
        }
    }
}


// 2. 일반도서 URL 생성 (1 ~ 985페이지)
const generalBase = "https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=25&ViewType=Detail&PublishMonth=0&SortOrder=5&Stockstatus=1&PublishDay=84&CID=50993&SearchOption=";
let generalUrls = [];

for (let page = 1; page <= 985; page++) {
    const url = `${generalBase}&page=${page}`;
    generalUrls.push(url);
}
console.log(`✅ 베스트셀러 URL ${urls.length}개`);
console.log(`✅ 일반도서 URL ${generalUrls.length}개`);
(async () => {
  for (let listUrl of urls) {
    try {
      const { data: html } = await axios.get(listUrl);

      const regex = /<a[^>]*href=["']([^"']+)["'][^>]*class=["'][^"']*\bbo3\b[^"']*["'][^>]*>/g;
      const links = [];
      let match;

      while ((match = regex.exec(html)) !== null) {
        const bookUrl = match[1];
        links.push(bookUrl);

        // ✅ 링크 하나마다 한 행씩 insert
        await db.execute(
          'INSERT INTO best_urls (urls) VALUES (?)',
          [bookUrl]
        );
      }

      console.log(`📄 목록 페이지: ${listUrl}`);
      console.log(`🔗 저장된 링크 수: ${links.length}`);
    } catch (err) {
      console.error(`❌ 요청 실패: ${listUrl}`, err.message);
    }
  }
  for (let listUrl of generalUrls) {
    try {
      const { data: html } = await axios.get(listUrl);

      const regex = /<a[^>]*href=["']([^"']+)["'][^>]*class=["'][^"']*\bbo3\b[^"']*["'][^>]*>/g;
      const links = [];
      let match;

      while ((match = regex.exec(html)) !== null) {
        const bookUrl = match[1];
        links.push(bookUrl);

        // ✅ 링크 하나마다 한 행씩 insert
        await db.execute(
          'INSERT INTO book_url (b_urls) VALUES (?)',
          [bookUrl]
        );
      }

      console.log(`📄 목록 페이지: ${listUrl}`);
      console.log(`🔗 저장된 링크 수: ${links.length}`);
    } catch (err) {
      console.error(`❌ 요청 실패: ${listUrl}`, err.message);
    }
  }

  await db.end(); // 연결 종료
})();