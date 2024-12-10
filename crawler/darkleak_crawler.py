import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# ChromeDriver 경로
current_dir = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

# TOR 프록시 설정
proxy_address = "127.0.0.1:9050"  # TOR SOCKS5 프록시 주소

# Selenium WebDriver 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")  # TOR 프록시 사용

# WebDriver 초기화
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 크롤링 대상 URL
base_url = "http://darkleakyqmv62eweqwy4dnhaijg4m4dkburo73pzuqfdumcntqdokyd.onion"
category_url = f"{base_url}/index.html"

# 데이터 저장용 리스트
all_data = []

def crawl_files():
    # Selenium으로 페이지 열기
    driver.get(category_url)
    time.sleep(5)  # 페이지 로딩 대기

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.find_all("tr", onclick=True)  # 클릭 가능한 행 추출

    for row in rows:
        try:
            file_name = row.find("strong").text.strip()  # 파일 이름 추출
            post_data = {"file_name": file_name}

            all_data.append(post_data)
            print(f"추출 완료: {file_name}")

        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")

    # JSON 파일로 저장
    with open("darkleak.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("darkleak.json 파일 저장 완료.")

if __name__ == "__main__":
    try:
        crawl_files()
    finally:
        # WebDriver 종료
        driver.quit()
