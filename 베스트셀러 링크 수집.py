from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# 크롬 드라이버 경로 #=======> 미노형 이거 필요한 건지는 모르겠지만, 일단 난 테스트할 때 내꺼 붙여넣어서 결과까지 확인했어. 예시 : C:/Users/taeyo/Downloads/chromedriver-win32/chromedriver-win32/chromedriver.exe
chrome_driver_path = " "

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--headless')  =======> 미노형 이건 걍 페이지 잘 굴러가고 있나 보는 게 맘 편할 거 같아서 걍 빼놓음

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

#  수집 대상 주차 생성
weeks_to_scrape = []
for year in range(2024, 2026):
    start_month = 4 if year == 2024 else 1
    end_month = 4 if year == 2025 else 4

    for month in range(start_month, end_month + 1):
        for week in range(1, 6):
            meta_info = f"{year}년{month}월{week}주"
            weeks_to_scrape.append((meta_info, year, month, week))

#  결과 저장
all_data = []

for meta_info, year, month, week in weeks_to_scrape:
    book_links_total = [f"[{meta_info}]"]

    for page in range(1, 21):
        url = (
            f"https://www.aladin.co.kr/shop/common/wbest.aspx?"
            f"BranchType=1&CID=50917&Year={year}&Month={month}&Week={week}"
            f"&BestType=Bestseller&SearchSubBarcode=&page={page}&cnt=50&SortOrder=1"
        )

        driver.get(url)
        time.sleep(1)            #=======> 미노형 로딩 시간은 테스트 차원에서 빨리 결과물 보고싶어서 1로 맞췄어어

        books = driver.find_elements(By.CSS_SELECTOR, "div.ss_book_list ul li a.bo3")

        if len(books) == 0:
            break

        for book in books:
            link = book.get_attribute("href")
            if link:
                book_links_total.append(link)

    if len(book_links_total) > 1:
        all_data.append(book_links_total)
        print(f"{year}년 {month}월 {week}주차 링크 {len(book_links_total) - 1}개 수집 완료")  

driver.quit()

#  파일 저장                       #=======> 미노형 내가 오라클 DB에 저장하는 구조를 잘 몰라서 함부로 못 건드리고 텍스트로 저장하는 올드한 방식으로 냅뒀어..
file_path = "book_links_by_week.txt"
with open(file_path, 'w', encoding='utf-8') as f:
    for week_data in all_data:
        for item in week_data:
            f.write(item + '\n')
        f.write('\n')