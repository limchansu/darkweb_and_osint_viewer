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

# 크롤링 대상 URL 카테고리 목록
categories = {
    "Accounts": "http://cislandpsv4xex2cy4t3vx4ogswq375fwnarmtfyarqek5ikxq57ioyd.onion/category/accounts/",
    "Combolists": "http://cislandpsv4xex2cy4t3vx4ogswq375fwnarmtfyarqek5ikxq57ioyd.onion/category/combolists/",
    "Packs": "http://cislandpsv4xex2cy4t3vx4ogswq375fwnarmtfyarqek5ikxq57ioyd.onion/category/packs/"
}

# 데이터 저장용 리스트
all_data = []

def crawl_category(category_name, base_url):
    for page_num in range(1, 11):  # 1번부터 10번 페이지까지
        try:
            url = f"{base_url}{page_num}"
            driver.get(url)
            time.sleep(5)  # 페이지 로딩 대기

            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(driver.page_source, "html.parser")
            posts = soup.find_all("a", class_="island-card-link")

            for post in posts:
                try:
                    title = post.find("h3", itemprop="headline").text.strip()
                    post_url = "http://cislandpsv4xex2cy4t3vx4ogswq375fwnarmtfyarqek5ikxq57ioyd.onion" + post["href"]
                    post_type = category_name
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
                    print(f"게시물 처리 중 오류 발생: {e}")

        except Exception as e:
            print(f"페이지 크롤링 중 오류 발생 (카테고리: {category_name}, 페이지: {page_num}): {e}")

def crawl_island():
    try:
        for category_name, base_url in categories.items():
            crawl_category(category_name, base_url)

        # JSON 파일로 저장 (주석 처리)
        # with open("island_data.json", "w", encoding="utf-8") as f:
        #     json.dump(all_data, f, ensure_ascii=False, indent=4)
        # print("island_data.json 파일 저장 완료.")

        return all_data

    finally:
        driver.quit()

if __name__ == "__main__":
    result = crawl_island()
    print(result)
