# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# import time
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# driver= webdriver.Chrome()
# driver.get('https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=362922298')
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
# time.sleep(2)  # 렌더링 기다림
# for i in range(2):
#     try:
#         print(f"⏳ 더보기 버튼 {i+1}번째 대기 중...")
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "Underline3_more"))
#         )

#         # 여기서 <a>가 동적으로 생기는 경우가 있음
#         WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, "#Underline3_more a"))
#         ).click()

#         print(f"✅ 더보기 버튼 {i+1}번째 클릭 완료")
#         time.sleep(2.5)
#     except Exception as e:
#         print(f"⚠️ 더보기 버튼 {i+1}번째 없음 또는 클릭 실패:", e)
#         break

# excerpt=driver.find_elements(By.XPATH, '//span[starts-with(@id, "u3_") and contains(@id, "_more")]')
# for elem in excerpt:
#     text = driver.execute_script("return arguments[0].innerText;", elem)
#     print(text.strip())

import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
sys.stdout.reconfigure(encoding="utf-8")  # ✅ 이 줄 추가
url = sys.argv[1]  # ✅ Node.js에서 넘긴 URL 받기
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)
driver.get(url)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
time.sleep(2)

for i in range(2):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Underline3_more"))
        )
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#Underline3_more a"))
        ).click()
        time.sleep(2)
    except:
        break

excerpts = driver.find_elements(By.XPATH, '//span[starts-with(@id, "u3_") and contains(@id, "_more")]')
texts = []
for elem in excerpts:
    text = driver.execute_script("return arguments[0].innerText;", elem)
    texts.append(text.strip())

driver.quit()

print("\n\n".join(texts),flush=True)
