from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# 크롬 드라이버 경로
chrome_driver_path = " "  # 여기에 경로 복붙

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--headless')  # =======> 미노형 이건 걍 페이지 잘 굴러가고 있나 보는 게 맘 편할 거 같아서 걍 빼놓음

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 결과 저장 리스트
all_data = []

# 페이지 순회
page = 1
while True:
    url = (
        f"https://www.aladin.co.kr/shop/wbrowse.aspx?"
        f"BrowseTarget=List&ViewRowsCount=50&ViewType=Detail&PublishMonth=0"
        f"&SortOrder=2&page={page}&Stockstatus=1&PublishDay=84&CID=50993&SearchOption="
    )

    driver.get(url)
    time.sleep(1)  # 이것도 빨리 결과 보고 싶어서 1초로

    books = driver.find_elements(By.CSS_SELECTOR, "div.ss_book_list ul li a.bo3")

    if len(books) == 0:
        break  # 더 이상 책이 없으면 루프 종료

    for book in books:
        link = book.get_attribute("href")
        if link:
            all_data.append(link)

    print(f"{page}페이지에서 {len(books)}개 링크 수집 완료 (누적 {len(all_data)}개)")
    page += 1  # 다음 페이지

driver.quit()

 #=======> 미노형 내가 오라클 DB에 저장하는 구조를 잘 몰라서 함부로 못 건드리고 텍스트로 저장하는 올드한 방식으로 냅뒀어..
file_path = "korean_novels_after_2000_links.txt"
with open(file_path, 'w', encoding='utf-8') as f:
    for link in all_data:
        f.write(link + '\n')

print(f"\n 총 {len(all_data)}개의 링크를 '{file_path}' 파일에 저장 완료.")