import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

async def fetch_page(session, url):
    """
    페이지 요청을 비동기적으로 처리
    """
    try:
        async with session.get(url, timeout=15) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"[ERROR] darknetARMY_crawler.py - fetch_page(): {e}")
        return None

async def process_page(db, session, base_url, page):
    """
    각 페이지를 비동기적으로 처리하고 MongoDB에 저장
    """
    collection = db["darknetARMY"]
    url = f"{base_url}page-{page}"

    html_content = await fetch_page(session, url)
    if not html_content:
        return

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')
    threads = soup.find_all('div', class_='structItem')

    for thread in threads:
        title_tag = thread.find('div', class_='structItem-title')
        title = title_tag.get_text(strip=True) if title_tag else None

        author_tag = thread.find('a', class_='username')
        author = author_tag.get_text(strip=True) if author_tag else None

        time_tag = thread.find('time')
        post_time = time_tag["title"] if time_tag and "title" in time_tag.attrs else None

        post_data = {
            "title": title,
            "author": author,
            "posted Time": post_time,
            "crawled Time": str(datetime.now())
        }

        # 중복 확인 및 저장
        if title and not collection.find_one({"title": title, "posted Time": post_time}):
            collection.insert_one(post_data)

async def darknetARMY(db):
    """
    DarknetARMY 크롤러 비동기 실행 및 MongoDB 저장
    """
    base_url = "http://dna777qhcrxy5sbvk7rkdd2phhxbftpdtxvwibih26nr275cdazx4uyd.onion/whats-new/posts/797681/"
    proxy_url = "socks5://127.0.0.1:9050"

    connector = ProxyConnector.from_url(proxy_url)
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [process_page(db, session, base_url, page) for page in range(1, 4)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # MongoDB 연결 설정
    MONGO_URI = "mongodb://localhost:27017/"
    DB_NAME = "darkweb_db"

    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]

        # 비동기 실행
        asyncio.run(darknetARMY(db))

    except Exception as e:
        print(f"[ERROR] darknetARMY_crawler.py - testing_main(): {e}")
