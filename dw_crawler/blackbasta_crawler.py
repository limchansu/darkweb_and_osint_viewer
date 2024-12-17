import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime
from pymongo import MongoClient

# JSON Schema 정의
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "description": {"type": "string"},
        "crawled_time": {"type": "string", "format": "date-time"},
    },
    "required": ["title", "url", "description"],
}

def crawl_page(category_url, proxy_address, schema, collection):
    """
    개별 페이지를 동기적으로 크롤링하는 함수
    """
    # Selenium WebDriver 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"[INFO] Crawling page: {category_url}")
        driver.get(category_url)

        # JavaScript 로딩 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "title"))
        )

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.find_all("div", class_="title")

        for post in posts:
            try:
                title_element = post.find("a", class_="blog_name_link")
                if not title_element:
                    continue

                title = title_element.text.strip()
                url = title_element["href"].strip()

                # Description 추출
                description_element = post.find_next("p", {"data-v-md-line": "3"})
                description = (
                    description_element.get_text(strip=True)
                    if description_element
                    else ""
                )

                # 데이터 생성
                post_data = {
                    "title": title,
                    "url": url,
                    "description": description,
                    "crawled_time": str(datetime.now()),
                }

                # JSON Schema 검증
                try:
                    validate(instance=post_data, schema=schema)

                    # 중복 확인 및 데이터 저장
                    if not collection.find_one({"title": title, "url": url}):
                        collection.insert_one(post_data)
                        print(f"[INFO] Saved: {title}")
                    else:
                        print(f"[INFO] Skipped (duplicate): {title}")

                except ValidationError as e:
                    print(f"[WARNING] 데이터 검증 실패: {e.message}")

            except Exception as e:
                print(f"[ERROR] 데이터 추출 중 오류 발생: {e}")

    except Exception as e:
        print(f"[ERROR] 페이지 크롤링 실패: {e}")

    finally:
        driver.quit()


async def blackbasta(db):
    """
    BlackBasta 크롤러 실행 및 MongoDB 컬렉션에 비동기적 저장
    """
    collection = db["blackbasta"]  # MongoDB 컬렉션 선택
    proxy_address = "127.0.0.1:9050"

    # 크롤링 대상 URL
    base_url = "http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion"
    category_url = f"{base_url}/"

    # 비동기 실행
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                crawl_page,
                category_url, proxy_address, schema, collection
            )
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    # MongoDB 연결 설정
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(blackbasta(db))
