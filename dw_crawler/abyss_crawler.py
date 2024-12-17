import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime
from jsonschema import validate, ValidationError
from pymongo import MongoClient

async def crawl_page(base_url, proxy_address, schema, collection, show):
    """
    개별 페이지를 크롤링하는 비동기 함수 (Playwright 사용)
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                proxy={
                    "server": f"socks5://{proxy_address}"
                }
            )
            page = await browser.new_page()
            await page.goto(base_url, timeout=60000)
            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")
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
                    if not await collection.find_one({"title": title, "description": description}):
                        obj = await collection.insert_one(post_data)
                        if show:
                            print('abyss insert success ' + str(obj.inserted_id))

                except ValidationError as ve:
                    print(f"[ERROR] abyss_crawler.py - crawl_page(): {ve.message}")

            except Exception as e:
                print(f"[ERROR] abyss_crawler.py - crawl_page(): {e}")

    except Exception as e:
        print(f"[ERROR] abyss_crawler.py - crawl_page(): {e}")

async def abyss(db, show=False):
    """
    Abyss 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장 (비동기 실행)
    """
    collection = db["abyss"]  # MongoDB 컬렉션 선택

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
    tasks = [
        crawl_page(url, proxy_address, schema, collection, show) for url in base_urls
    ]
    await asyncio.gather(*tasks)

