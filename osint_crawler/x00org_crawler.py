import asyncio
import aiohttp
import json
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime
from stem import Signal
from stem.control import Controller
from pymongo import MongoClient

# Tor 네트워크를 재시작하여 새로운 IP 할당
def renew_connection(password):
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=password)
            controller.signal(Signal.NEWNYM)
            print("New Tor connection requested.")
    except Exception as e:
        print(f"Failed to renew Tor connection: {e}")

# 키워드 로드 함수
def load_keywords(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get("keywords", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading keywords from {file_path}: {e}")
        return []

# Tor 프록시를 통한 비동기 요청 함수
async def tor_request(session, url, retries=3):
    proxy = "socks5h://127.0.0.1:9050"
    for attempt in range(retries):
        try:
            await asyncio.sleep(3)  # 요청 간 딜레이 추가
            async with session.get(url, proxy=proxy, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Failed to fetch {url}, status: {response.status}")
        except Exception as e:
            print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
    return None

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
    for keyword in keywords:
        if content.lower().count(keyword.lower()) >= 3:
            return True
    return False

# 크롤링 실행 함수
async def run(db):
    collection = db["0x00org"]  # MongoDB 컬렉션 선택
    keywords_file = "./cleaned_keywords.json"
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

    keywords = load_keywords(keywords_file)
    if not keywords:
        print("No keywords found. Exiting.")
        return

    async with aiohttp.ClientSession() as session:
        for base_url in base_urls:
            print(f"Fetching post titles from {base_url}...")
            posts = await fetch_post_titles(session, base_url)
            if not posts:
                print(f"No posts found for {base_url}. Skipping.")
                continue

            print("Matching keywords in titles...")
            matched_posts = match_keywords_in_titles(posts, keywords)

            print("Verifying keyword matches in content and saving to MongoDB...")
            tasks = []
            for post in matched_posts:
                tasks.append(asyncio.create_task(
                    verify_and_save(session, collection, post, keywords)
                ))

            await asyncio.gather(*tasks)

# 본문 검증 및 저장 함수
async def verify_and_save(session, collection, post, keywords):
    if await verify_keywords_in_content(session, post["url"], keywords):
        if not collection.find_one({"title": post["title"]}):
            post_data = {
                "title": post["title"],
                "url": post["url"],
                "keywords": post["keywords"],
                "crawled_time": str(datetime.now())
            }
            collection.insert_one(post_data)
            print(f"Saved: {post['title']}")
        else:
            print(f"Skipped (duplicate): {post['title']}")

if __name__ == "__main__":
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    renew_connection(password="your_password")  # Tor 재연결
    asyncio.run(run(db))
