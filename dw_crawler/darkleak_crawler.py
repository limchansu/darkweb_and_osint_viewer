import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient  # 비동기 MongoDB 클라이언트

# JSON Schema 정의
SCHEMA = {
    "type": "object",
    "properties": {
        "file_name": {"type": "string"},
        "url": {"type": ["string", "null"]},
        "crawled_time": {"type": "string"}
    },
    "required": ["file_name", "url"]
}

# TOR Proxy 설정
TOR_PROXY = "socks5://127.0.0.1:9050"

async def fetch_page(page, url):
    """
    Playwright를 사용해 페이지를 가져오는 비동기 함수
    """
    try:
        print(f"[INFO] Fetching URL: {url}")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)  # 페이지 로드 대기
        return await page.content()
    except Exception as e:
        print(f"[ERROR] darkleak_crawler.py - fetch_page(): {e}")
        return None

async def process_page(db, html, base_url):
    """
    HTML을 파싱하고 데이터를 MongoDB에 저장하는 함수
    """
    collection = db["darkleak"]
    try:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr", onclick=True)

        for row in rows:
            try:
                # 파일 이름 추출
                file_name = row.find("strong").text.strip()

                # onclick 속성에서 URL 추출
                onclick_attr = row.get("onclick")
                if onclick_attr and "window.location='" in onclick_attr:
                    relative_url = onclick_attr.split("'")[1]
                    full_url = f"{base_url}/{relative_url}"
                else:
                    full_url = None

                # 데이터 생성
                post_data = {
                    "file_name": file_name,
                    "url": full_url,
                    "crawled_time": str(datetime.now())
                }

                # JSON Schema 검증
                validate(instance=post_data, schema=SCHEMA)

                # 중복 확인 및 데이터 저장
                if not await collection.find_one({"file_name": file_name, "url": full_url}):
                    await collection.insert_one(post_data)
                    print(f"[INFO] Saved: {file_name}")
            except ValidationError as e:
                print(f"[ERROR] darkleak_crawler.py - process_page(): {e.message}")
            except Exception as e:
                print(f"[ERROR] darkleak_crawler.py - process_page(): {e}")

    except Exception as e:
        print(f"[ERROR] darkleak_crawler.py - process_page(): {e}")

async def darkleak(db):
    """
    DarkLeak 크롤러 실행 (비동기)
    """
    base_url = "http://darkleakyqmv62eweqwy4dnhaijg4m4dkburo73pzuqfdumcntqdokyd.onion"
    category_url = f"{base_url}/index.html"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, proxy={"server": TOR_PROXY})
            page = await browser.new_page()

            # 페이지 가져오기
            html = await fetch_page(page, category_url)
            if html:
                # 페이지 처리 및 데이터 저장
                await process_page(db, html, base_url)

            await browser.close()
    except Exception as e:
        print(f"[ERROR] darkleak_crawler.py - darkleak(): {e}")

if __name__ == "__main__":
    # 비동기 MongoDB 연결
    MONGO_URI = "mongodb://localhost:27017"
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(darkleak(db))
