import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from stem import Signal
from stem.control import Controller
import os

# Tor 네트워크를 재시작하여 새로운 IP 할당
async def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="your_password")  # 비밀번호 설정 필요
        controller.signal(Signal.NEWNYM)
        print("[INFO] New Tor connection requested.")

# Tor 프록시를 통한 비동기 요청 함수
async def tor_request(session, url):
    proxies = 'socks5h://127.0.0.1:9050'
    try:
        async with session.get(url, proxy=proxies, timeout=30) as response:
            if response.status == 200:
                return await response.text()
            print(f"[WARNING] Failed to fetch {url}, status: {response.status}")
    except Exception as e:
        print(f"[ERROR] Request failed for {url}: {e}")
    return None

# 페이지 크롤링 함수
async def search_page(session, db, target_url, keywords):
    collection = db["tuts4you"]  # MongoDB 컬렉션 선택
    print(f"[INFO] Scraping URL: {target_url}")

    try:
        html_content = await tor_request(session, target_url)
        if not html_content:
            return
        
        soup = BeautifulSoup(html_content, "html.parser")
        total_pages = get_total_pages(soup)
        print(f"[INFO] Total pages to scrape: {total_pages}")

        for page_num in range(1, total_pages + 1):
            page_url = f"{target_url}page/{page_num}/" if page_num > 1 else target_url
            print(f"[INFO] Scraping page {page_num}: {page_url}")

            page_content = await tor_request(session, page_url)
            if not page_content:
                continue

            soup = BeautifulSoup(page_content, "html.parser")
            a_tags = soup.find_all("a")

            for a_tag in a_tags:
                if check_page(a_tag, keywords) and check_snippet_for_keywords(a_tag, keywords):
                    title = a_tag.get("title")
                    url = a_tag.get("href")
                    if not await collection.find_one({"title": title}):  # 중복 확인
                        post_data = {
                            "title": title,
                            "url": url,
                            "crawled_time": str(datetime.utcnow())
                        }
                        await collection.insert_one(post_data)
                        print(f"[INFO] Saved: {title}")
    except Exception as e:
        print(f"[ERROR] Error occurred while scraping {target_url}: {e}")

# 페이지 수 가져오기
def get_total_pages(soup):
    pagination_element = soup.find("li", class_="ipsPagination_pageJump")
    if pagination_element:
        match = re.search(r"Page \d+ of (\d+)", pagination_element.get_text(strip=True))
        if match:
            return int(match.group(1))
    return 1

# 키워드 필터링 함수
def check_page(a_tag, keywords):
    return any(keyword in a_tag.get("title", "") for keyword in keywords)

def check_snippet_for_keywords(a_tag, keywords):
    parent_div = a_tag.find_parent("div", class_="ipsTopicSnippet__top")
    if parent_div:
        snippet_p = parent_div.find_next_sibling("div", class_="ipsTopicSnippet__snippet")
        if snippet_p:
            snippet_text = snippet_p.get_text(strip=True)
            return sum(1 for keyword in keywords if keyword in snippet_text) >= 5
    return False

# 메인 실행 함수
async def run():
    # MongoDB 연결
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["darkweb_db"]

    # 현재 스크립트 기준 경로에서 키워드 불러오기
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KEYWORDS_FILE = os.path.join(BASE_DIR, "cleaned_keywords.json")
    with open(KEYWORDS_FILE, 'r') as dictionary_json:
        data = json.load(dictionary_json)
    keywords = data.get("keywords", [])

    # 타겟 URL 목록
    target_categories = [
        "https://forum.tuts4you.com/forum/47-programming-and-coding/",
        "https://forum.tuts4you.com/forum/121-programming-resources/",
        "https://forum.tuts4you.com/forum/133-software-security/",
        "https://forum.tuts4you.com/forum/146-challenge-of-reverse-engineering/",
        "https://forum.tuts4you.com/forum/124-hardware-reverse-engineering/",
        "https://forum.tuts4you.com/forum/122-network-security/",
        "https://forum.tuts4you.com/forum/93-reverse-engineering-articles/"
    ]

    # Tor 연결 갱신
    await renew_connection()

    # 비동기 세션 생성
    connector = ProxyConnector.from_url('socks5h://127.0.0.1:9050')
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [search_page(session, db, url, keywords) for url in target_categories]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run())
