import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from stem import Signal
from stem.control import Controller
from datetime import datetime


# Tor 네트워크를 재시작하여 새로운 IP 할당
def renew_connection(password):
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=password)
            controller.signal(Signal.NEWNYM)
            print("New Tor connection requested.")
    except Exception as e:
        print(f"Failed to renew Tor connection: {e}")


# Tor 프록시를 통한 요청 함수
def tor_request(url, headers=None, retries=3):
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(3, 8))  # 요청 간 딜레이 추가
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt == retries - 1:
                return None


# 키워드 로드 함수
def load_keywords(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get("keywords", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading keywords from {file_path}: {e}")
        return []


# 게시글 제목 및 URL 가져오기
def fetch_post_titles(base_url):
    response = tor_request(base_url)
    if not response:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    posts = [
        {
            "title": link.get_text(strip=True),
            "url": link['href']
        }
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
def verify_keywords_in_content(url, keywords):
    response = tor_request(url)
    if not response:
        return False

    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text(strip=True)
    for keyword in keywords:
        if content.lower().count(keyword.lower()) >= 3:
            return True
    return False


# 크롤링 실행 함수
def run(db):
    """
    0x00org 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["0x00org"]  # MongoDB 컬렉션 선택
    keywords_file = "cleaned_keywords.json"
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

    for base_url in base_urls:
        print(f"Fetching post titles from {base_url}...")
        posts = fetch_post_titles(base_url)
        if not posts:
            print(f"No posts found for {base_url}. Skipping.")
            continue

        print("Matching keywords in titles...")
        matched_posts = match_keywords_in_titles(posts, keywords)

        print("Verifying keyword matches in content and saving to MongoDB...")
        for post in matched_posts:
            if verify_keywords_in_content(post["url"], post["keywords"].split(", ")):
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
