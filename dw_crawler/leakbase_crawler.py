import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from motor.motor_asyncio import AsyncIOMotorClient


async def setup_database(db_name, collection_names):
    client = AsyncIOMotorClient("mongodb://mongo1:30001,mongo2:30002,mongo:30003/?replicaSet=my-rs")
    db = client[db_name]
    existing_collections = await db.list_collection_names()
    for collection in collection_names:
        if collection not in existing_collections:
            await db.create_collection(collection)
            print(f"[INFO] {collection} 컬렉션 생성 완료! ({db_name})")
    print(f"[INFO] MongoDB 설정 완료: {db_name}")
    return db


async def leakbase(db):
    collection = db["leakbase"]
    url = "https://leakbase.io/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"})
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector("li._xgtIstatistik-satir")

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            posts = soup.find_all("li", class_="_xgtIstatistik-satir")

            for post in posts:
                title_tag = post.find("div", class_="_xgtIstatistik-satir--konu")
                title = title_tag.text.strip() if title_tag else None

                author_tag = post.find("div", class_="_xgtIstatistik-satir--hucre _xgtIstatistik-satir--sonYazan")
                author = author_tag.find("a", class_="username").text.strip() if author_tag and author_tag.find("a") else None

                time_tag = post.find("div", class_="_xgtIstatistik-satir--zaman")
                post_time = time_tag.text.strip() if time_tag else None

                post_data = {
                    "title": title,
                    "author": author,
                    "posted_time": post_time,
                    "crawled_time": str(datetime.now()),
                }

                if title and not await collection.find_one({"title": title}):
                    await collection.insert_one(post_data)
                    print(f"데이터 저장 완료: {title}")
                else:
                    print(f"중복 데이터로 저장 건너뜀: {title}")

        except Exception as e:
            print(f"오류 발생: {e}")
        finally:
            await browser.close()



