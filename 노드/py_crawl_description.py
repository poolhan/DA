# py_crawl_description.py

import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

sys.stdout.reconfigure(encoding="utf-8")

url = sys.argv[1]  # Node.js에서 넘긴 URL
# url="https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=278770576"
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)
driver.get(url)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
time.sleep(1)

book_description = ""
containers = driver.find_elements(By.CLASS_NAME, "Ere_prod_mconts_box")

for container in containers:
    try:
        label = container.find_element(By.CLASS_NAME, "Ere_prod_mconts_LS")
        if "책소개" in label.text:
            content_div = container.find_element(By.CLASS_NAME, "Ere_prod_mconts_R")
            book_description = content_div.text.strip()
            break
    except:
        continue

driver.quit()
print(book_description, flush=True)

