import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
import time

# ChromeDriver 경로 (프로젝트 폴더 내에 위치한 chromedriver.exe)
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

# 크롤링 대상 URL (onion 사이트)
base_url = "https://crackingisland.net/"  # onion 사이트 URL로 변경
category_url = f"{base_url}/categories/combolists"

# JSON Schema 정의
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "url": {"type": "string"},
        "type": {"type": "string"},
        "dateCreated": {"type": "string"},
        "description": {"type": "string"}
    },
    "required": ["title", "url", "type", "dateCreated", "description"]
}

# 데이터 저장용 리스트
all_data = []

def crawl_combolists():
    try:
        # Selenium으로 페이지 열기
        driver.get(category_url)
        # JavaScript 로딩 대기
        time.sleep(5)

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.find_all("a", itemprop="url")

        for post in posts:
            try:
                title = post.find("h2", itemprop="headline").text.strip()
                post_url = base_url + post["href"]
                post_type = post.find("span", itemprop="about").text.strip()
                post_date = post.find("span", itemprop="dateCreated").text.strip()
                description = post.find("p", itemprop="text").text.strip()

                # 데이터 저장
                post_data = {
                    "title": title,
                    "url": post_url,
                    "type": post_type,
                    "dateCreated": post_date,
                    "description": description,
                }

                # JSON Schema 검증
                try:
                    validate(instance=post_data, schema=schema)
                    all_data.append(post_data)
                    print(f"추출 완료: {title}")
                except ValidationError as e:
                    print(f"데이터 검증 실패: {e.message}")

            except Exception as e:
                print(f"크롤링 중 오류 발생: {e}")

        # JSON 파일로 저장 (주석 처리)
        # with open("test.json", "w", encoding="utf-8") as f:
        #     json.dump(all_data, f, ensure_ascii=False, indent=4)
        # print("test.json 파일 저장 완료.")

        return all_data

    finally:
        driver.quit()

if __name__ == "__main__":
    result = crawl_combolists()
    print(result)
