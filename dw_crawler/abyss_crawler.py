import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
from jsonschema import validate, ValidationError
from pymongo import MongoClient


def crawl_page(base_url, chromedriver_path, proxy_address, schema, collection):
    """
    개별 페이지를 크롤링하는 동기 함수
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창 표시 없이 실행
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(base_url)
        driver.implicitly_wait(5)  # 페이지 로딩 대기

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.find_all("div", class_="card-body")  # 카드 데이터 추출

        for card in cards:
            try:
                # 데이터 추출
                title = card.find("h5", class_="card-title").text.strip()
                description = card.find("p", class_="card-text").text.strip()

                # 데이터 생성
                post_data = {
                    "title": title,
                    "description": description,
                    "crawled_time": str(datetime.now())
                }

                # JSON Schema 검증
                try:
                    validate(instance=post_data, schema=schema)

                    # 중복 확인 및 데이터 저장
                    if not collection.find_one({"title": title, "description": description}):
                        collection.insert_one(post_data)
                    else:

                except ValidationError as ve:
                    print(f"[ERROR] abyss_crawler.py - crawl_page(): {ve.message}")

            except Exception as e:
                print(f"[ERROR] abyss_crawler.py - crawl_page(): {e}")

    except Exception as e:
        print(f"[ERROR] abyss_crawler.py - crawl_page(): {e}")
    finally:
        driver.quit()


async def abyss(db):
    """
    Abyss 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장 (비동기 실행)
    """
    collection = db["abyss"]  # MongoDB 컬렉션 선택

    # ChromeDriver 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

    # 프록시 주소 (Tor SOCKS5)
    proxy_address = "127.0.0.1:9050"

    # JSON Schema 정의
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "crawled_time": {"type": "string"}
        },
        "required": ["title", "description"]
    }

    # 대상 URL 목록 (명세 준수)
    base_urls = [
        "http://3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd.onion"
    ]

    # 비동기 실행
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                crawl_page,
                url, chromedriver_path, proxy_address, schema, collection
            )
            for url in base_urls
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    # MongoDB 연결 설정
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(abyss(db))
