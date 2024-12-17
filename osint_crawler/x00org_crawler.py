import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# Tor 프록시 설정
PROXY_URL = "socks5://127.0.0.1:9050"

# 비동기 Tor 요청 함수
async def tor_request(session, url, retries=3):
    for attempt in range(retries):
        try:
            await asyncio.sleep(2)  # 요청 간 딜레이 추가
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"[ERROR] x00org_crawler.py - tor_request(){e}")
    return None

# 키워드 로드 함수
def load_keywords(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get("keywords", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] x00org_crawler.py - load_keywords(): {e}")
        return []

# 게시글 제목 및 URL 가져오기
async def fetch_post_titles(session, base_url):
    html_content = await tor_request(session, base_url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    posts = [
        {"title": link.get_text(strip=True), "url": link['href']}
        for link in soup.find_all('a', class_='title raw-link raw-topic-link', href=True)
    ]
    return posts

# 제목에서 키워드 매칭 확인
def match_keywords_in_titles(posts, keywords):
    results = []
    for post in posts:
        matched_keywords = [
            keyword for keyword in keywords
            if re.search(rf"\b{re.escape(keyword).replace(' ', '[-_]')}\b", post['title'], re.IGNORECASE)
        ]
        if matched_keywords:
            results.append({
                "title": post["title"],
                "keywords": ", ".join(matched_keywords),
                "url": post["url"]
            })
    return results

# 본문에서 키워드 매칭 확인
async def verify_keywords_in_content(session, url, keywords):
    html_content = await tor_request(session, url)
    if not html_content:
        return False

    soup = BeautifulSoup(html_content, 'html.parser')
    content = soup.get_text(strip=True)
    return any(content.lower().count(keyword.lower()) >= 3 for keyword in keywords)

# 크롤링 실행 함수
async def x00org(db, show=False):
    collection = db["x00org"]

    # 키워드 파일 로드
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KEYWORDS_FILE = os.path.join(BASE_DIR, "cleaned_keywords.json")
    keywords = load_keywords(KEYWORDS_FILE)
    if not keywords:
        return

    base_urls = [
        "https://0x00sec.org/c/bug-bounty/108",
        "https://0x00sec.org/c/pentesting/101",
        "https://0x00sec.org/c/red-team/102",
        "https://0x00sec.org/c/blue-team/105",
        "https://0x00sec.org/c/exploit-development/53",
        "https://0x00sec.org/c/reconnaissance/54",
        "https://0x00sec.org/c/malware/56",
        "https://0x00sec.org/c/cryptology/57",
        "https://0x00sec.org/c/reverse-engineering/58",
        "https://0x00sec.org/c/linux/64",
        "https://0x00sec.org/c/ai/71",
        "https://0x00sec.org/c/social/46",
        "https://0x00sec.org/c/uncategorized/1",
        "https://0x00sec.org/c/ctf/55",
        "https://0x00sec.org/c/web-hacking/59",
        "https://0x00sec.org/c/social-engineering/60",
        "https://0x00sec.org/c/programming/61",
        "https://0x00sec.org/c/databases/62",
        "https://0x00sec.org/c/networking/63",
        "https://0x00sec.org/c/algorithms/70",
        "https://0x00sec.org/c/anonymity/72",
        "https://0x00sec.org/c/hardware/68",
        "https://0x00sec.org/c/operations/86",
        "https://0x00sec.org/c/phone-hacking/92",
        "https://0x00sec.org/c/forensics/106"
    ]

    # Tor 프록시 커넥터 생성
    connector = ProxyConnector.from_url(PROXY_URL)

    async with aiohttp.ClientSession(connector=connector) as session:
        for base_url in base_urls:
            posts = await fetch_post_titles(session, base_url)
            if not posts:
                continue

            matched_posts = match_keywords_in_titles(posts, keywords)
            for post in matched_posts:
                if await verify_keywords_in_content(session, post["url"], post["keywords"].split(", ")):
                    post_data = {
                        "title": post["title"],
                        "url": post["url"],
                        "keywords": post["keywords"],
                        "crawled_time": str(datetime.now())
                    }
                    if show:
                        print(f'github: {post_data}')
                    if not await collection.find_one({"title": post["title"]}):


                        obj = await collection.insert_one(post_data)
                        if show:
                            print('x00org insert success ' + str(obj.inserted_id))

