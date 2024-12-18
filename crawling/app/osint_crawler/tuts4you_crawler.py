import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
import json
import os
import re
from .config import TOR_PROXY

# 비동기 Tor 요청 함수
async def tor_request(session, url):
    try:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"[ERROR] tuts4you_crawler.py - tor_request(): {e}")
    return None

# 페이지 수 추출 함수
def get_total_pages(soup):
    pagination_element = soup.find("li", class_="ipsPagination_pageJump")
    if pagination_element:
        text = pagination_element.get_text(strip=True)
        match = re.search(r"Page \d+ of (\d+)", text)
        if match:
            return int(match.group(1))
    return 1

# 키워드 검사 함수
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

# 페이지 크롤링 함수
async def search_page(session, collection, target_url, keywords, show):
    
    try:
        html_content = await tor_request(session, target_url)
        if not html_content:
            return

        soup = BeautifulSoup(html_content, "html.parser")
        total_pages = get_total_pages(soup)

        for page_num in range(1, total_pages + 1):
            page_url = f"{target_url}page/{page_num}/" if page_num > 1 else target_url

            page_content = await tor_request(session, page_url)
            if not page_content:
                continue

            soup = BeautifulSoup(page_content, "html.parser")
            a_tags = soup.find_all("a")

            for a_tag in a_tags:
                if check_page(a_tag, keywords) and check_snippet_for_keywords(a_tag, keywords):
                    title = a_tag.get("title")
                    url = a_tag.get("href")
                    post_data = {
                        "title": title,
                        "url": url,
                    }
                    if show:
                        print(f'tuts4you: {post_data}')
                    if not await collection.find_one({"title": title}):  # 중복 확인
                        obj = await collection.insert_one(post_data)
                        if show:
                            print('tuts4you insert success ' + str(obj.inserted_id))
    except Exception as e:
        print(f"[ERROR] tuts4you_crawler.py - search_page(): {e}")


async def tuts4you(db, show=False):
    collection = db["tuts4you"]
    # 현재 스크립트 기준 경로에서 키워드 파일 로드
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KEYWORDS_FILE = os.path.join(BASE_DIR, "cleaned_keywords.json")
    
    try:
        with open(KEYWORDS_FILE, 'r') as f:
            data = json.load(f)
        keywords = data.get("keywords", [])
    except FileNotFoundError as e:
        print(f"[ERROR] tuts4you_crawler.py - tuts4you(): {e}")
        return

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

    # Tor 프록시 커넥터 생성
    connector = ProxyConnector.from_url(TOR_PROXY)

    # 비동기 세션 생성 및 크롤링 작업 수행
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [search_page(session, collection, url, keywords, show) for url in target_categories]
        await asyncio.gather(*tasks)
