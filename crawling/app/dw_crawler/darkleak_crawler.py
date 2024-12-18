import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient  # 비동기 MongoDB 클라이언트
from .config import TOR_PROXY
# JSON Schema 정의
SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "url": {"type": ["string", "null"]},
        "crawled_time": {"type": "string"}
    },
    "required": ["title", "url"]
}


async def fetch_page(page, url):
    """
    Playwright를 사용해 페이지를 가져오는 비동기 함수
    """
    try:
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)  # 페이지 로드 대기
        return await page.content()

    except Exception as e:
        print(f"[ERROR] darkleak_crawler.py - fetch_page(): {e}")
        return None

async def process_page(db, html, base_url, show):
    """
    HTML을 파싱하고 데이터를 MongoDB에 저장하는 함수
    """
    collection = db["darkleak"]
    try:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr", onclick=True)

        for row in rows:
            try:
                # 제목(title) 추출
                title = row.find("strong").text.strip()

                # onclick 속성에서 URL 추출
                onclick_attr = row.get("onclick")
                if onclick_attr and "window.location='" in onclick_attr:
                    relative_url = onclick_attr.split("'")[1]
                    full_url = f"{base_url}/{relative_url}"
                else:
                    full_url = None

                # 데이터 생성
                post_data = {
                    "title": title,
                    "url": full_url,
                }

                # JSON Schema 검증
                validate(instance=post_data, schema=SCHEMA)
                if show:
                    print(f'darkleak: {post_data}')
                # 중복 확인 및 데이터 저장
                if not await collection.find_one({"title": title, "url": full_url}):
                    obj = await collection.insert_one(post_data)
                    if show:
                        print('darkleak insert success ' + str(obj.inserted_id))

            except ValidationError as e:
                print(f"[ERROR] darkleak_crawler.py - process_page(): {e.message}")
            except Exception as e:
                print(f"[ERROR] darkleak_crawler.py - process_page(): {e}")

    except Exception as e:
        print(f"[ERROR] darkleak_crawler.py - process_page(): {e}")

async def darkleak(db, show=False):
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
                await process_page(db, html, base_url, show)

            await browser.close()
    except Exception as e:
        print(f"[ERROR] darkleak_crawler.py - darkleak(): {e}")
