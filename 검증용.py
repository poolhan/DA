from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# 크롬 드라이버 경로
chrome_driver_path = "C:/Users/taeyo/Downloads/chromedriver-win32/chromedriver-win32/chromedriver.exe"  # 끝에 공백 지워줬어

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--headless')  # 필요시 주석 해제 가능

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 결과 저장 리스트
all_data = []

# ✅ 1페이지 ~ 5페이지까지만 순회
for page in range(1, 6):
    url = (
        f"https://www.aladin.co.kr/shop/wbrowse.aspx?"
        f"BrowseTarget=List&ViewRowsCount=50&ViewType=Detail&PublishMonth=0"
        f"&SortOrder=2&page={page}&Stockstatus=1&PublishDay=84&CID=50993&SearchOption="
    )

    driver.get(url)
    time.sleep(1)  # 로딩 대기

    books = driver.find_elements(By.CSS_SELECTOR, "div.ss_book_list ul li a.bo3")

    if len(books) == 0:
        print(f"{page}페이지에 책이 없어서 중단")
        break

    for book in books:
        link = book.get_attribute("href")
        if link:
            all_data.append(link)

    print(f"{page}페이지에서 {len(books)}개 링크 수집 완료 (누적 {len(all_data)}개)")

driver.quit()

# 파일 저장
file_path = "sample_korean_novels_links.txt"
with open(file_path, 'w', encoding='utf-8') as f:
    for link in all_data:
        f.write(link + '\n')

print(f"\n✅ 총 {len(all_data)}개의 링크를 '{file_path}' 파일에 저장 완료했습니다.")