import requests
from bs4 import BeautifulSoup
import json
import time
import re
from stem import Signal
from stem.control import Controller
from datetime import datetime


# Tor 네트워크를 재시작하여 새로운 IP 할당
def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='')  # Tor 비밀번호 설정 (torrc 파일 참고)
        controller.signal(Signal.NEWNYM)
        print("New Tor connection requested.")


# Tor 프록시를 통한 요청 함수
def tor_request(url, headers=None):
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
    return response


# 초기에 페이지 수를 가져오는 함수
def get_total_pages(soup):
    pagination_element = soup.find("li", class_="ipsPagination_pageJump")
    if pagination_element:
        text = pagination_element.get_text(strip=True)
        match = re.search(r"Page \d+ of (\d+)", text)
        if match:
            return int(match.group(1))
    return 1  # 페이지 번호가 없으면 1페이지로 가정


# 게시글 필터링 함수
def check_page(a_tag, keywords):
    for keyword in keywords:
        if keyword in a_tag.get("title", ""):
            return True
    return False


def check_snippet_for_keywords(a_tag, keywords):
    parent_div = a_tag.find_parent("div", class_="ipsTopicSnippet__top")
    if parent_div:
        snippet_p = parent_div.find_next_sibling("div", class_="ipsTopicSnippet__snippet")
        if snippet_p:
            snippet_text = snippet_p.get_text(strip=True)
            keyword_count = sum(1 for keyword in keywords if keyword in snippet_text)
            return keyword_count >= 5
    return False


# 페이지 크롤링 함수
def search_page(db, target_url, keywords):
    collection = db["tuts4you"]  # MongoDB 컬렉션 선택

    try:
        response = tor_request(target_url)
        if response.status_code != 200:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        total_pages = get_total_pages(soup)
        print(f"Total pages to scrape: {total_pages}")

        for page_num in range(1, total_pages + 1):
            page_url = f"{target_url}page/{page_num}/" if page_num > 1 else target_url
            print(f"Scraping page {page_num}: {page_url}")

            response = tor_request(page_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                a_tags = soup.find_all("a")

                filtered_links = []
                for a_tag in a_tags:
                    if check_page(a_tag, keywords) and check_snippet_for_keywords(a_tag, keywords):
                        filtered_links.append({"title": a_tag.get("title"), "url": a_tag.get("href")})

                for link in filtered_links:
                    if not collection.find_one({"title": link["title"]}):
                        post_data = {
                            "title": link["title"],
                            "url": link["url"],
                            "crawled_time": str(datetime.now())
                        }
                        collection.insert_one(post_data)
                        print(f"Saved: {link['title']}")
                    else:
                        print(f"Skipped (duplicate): {link['title']}")

            else:
                print(f"Failed to fetch page {page_num}. Status code: {response.status_code}")
                break

    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(2)


# 메인 실행 함수
async def run(db):
    """
    Tuts4You 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    with open("./cleaned_keywords.json", 'r') as dictionary_json:
        data = json.load(dictionary_json)
    keywords = data.get("keywords", [])

    target_categories = [
        "https://forum.tuts4you.com/forum/47-programming-and-coding/",
        "https://forum.tuts4you.com/forum/121-programming-resources/",
        "https://forum.tuts4you.com/forum/133-software-security/",
        "https://forum.tuts4you.com/forum/146-challenge-of-reverse-engineering/",
        "https://forum.tuts4you.com/forum/124-hardware-reverse-engineering/",
        "https://forum.tuts4you.com/forum/122-network-security/",
        "https://forum.tuts4you.com/forum/93-reverse-engineering-articles/"
    ]

    renew_connection()  # Tor 연결 초기화
    for category in target_categories:
        search_page(db, target_url=category, keywords=keywords)
