import requests
from bs4 import BeautifulSoup
import json
import time
import re
from stem import Signal
from stem.control import Controller

# Tor 네트워크를 재시작하여 새로운 IP 할당
def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='')  # 비밀번호 설정 (torrc 파일에서 설정하지 않았다면 빈 문자열)
        controller.signal(Signal.NEWNYM)
        print("New Tor connection requested.")

# Tor 프록시를 통한 요청 함수
def tor_request(url, headers=None):
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    response = requests.get(url, headers=headers, proxies=proxies, timeout=30)  # 30초로 증가
    return response

# 대상 URL 리스트
target_categories = [
    "https://forum.tuts4you.com/forum/47-programming-and-coding/",
    "https://forum.tuts4you.com/forum/121-programming-resources/",
    "https://forum.tuts4you.com/forum/133-software-security/",
    "https://forum.tuts4you.com/forum/146-challenge-of-reverse-engineering/",
    "https://forum.tuts4you.com/forum/124-hardware-reverse-engineering/",
    "https://forum.tuts4you.com/forum/122-network-security/",
    "https://forum.tuts4you.com/forum/93-reverse-engineering-articles/"
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
JSON_FILE_PATH = "./dictionary.json"

# 키워드 확인 및 첫 번째 필터링
def check_page(a_tag, keywords):
    for keyword in keywords:
        if keyword in a_tag.get("title", ""):
            return True  # 키워드가 포함된 경우 True 반환
    return False

# 두 번째 필터링: 해당 `a` 태그 근처의 `p` 태그에서 키워드 포함 확인
def check_snippet_for_keywords(a_tag, keywords):
    parent_div = a_tag.find_parent("div", class_="ipsTopicSnippet__top")  # `a` 태그의 상위 div 탐색
    if parent_div:
        snippet_p = parent_div.find_next_sibling("div", class_="ipsTopicSnippet__snippet")
        if snippet_p:
            snippet_text = snippet_p.get_text(strip=True)
            keyword_count = sum(1 for keyword in keywords if keyword in snippet_text)
            return keyword_count >= 3  # 키워드가 3개 이상 포함된 경우 True 반환
    return False

# 페이지 수를 가져오는 함수
def get_total_pages(soup):
    pagination_element = soup.find("li", class_="ipsPagination_pageJump")
    if pagination_element:
        text = pagination_element.get_text(strip=True)
        match = re.search(r"Page \d+ of (\d+)", text)
        if match:
            return int(match.group(1))  # 마지막 페이지 번호 반환
    return 1  # 페이지 번호가 없으면 1페이지로 가정

# 페이지 검색
def search_page(target_url):
    with open(JSON_FILE_PATH, 'r') as dictionary_json:
        data = json.load(dictionary_json)
    keywords = data.get("keywords", [])

    try:
        # 첫 페이지로 접속해 전체 페이지 수 가져오기
        response = tor_request(target_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        total_pages = get_total_pages(soup)
        print(f"Total pages to scrape: {total_pages}")

        for page_num in range(1, total_pages + 1):
            if page_num > 1:
                page_url = f"{target_url}page/{page_num}/"
            else:
                page_url = target_url
            print(f"Scraping page {page_num}: {page_url}")
            
            # Tor 네트워크를 통한 요청
            response = tor_request(page_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                a_tags = soup.find_all("a")

                filtered_links = []
                for a_tag in a_tags:
                    if check_page(a_tag, keywords):
                        if check_snippet_for_keywords(a_tag, keywords):
                            filtered_links.append({"title": a_tag.get("title"), "url": a_tag.get("href")})

                if filtered_links:
                    for link in filtered_links:
                        print(f"Title: {link['title']}\nLink: {link['url']}\n")
                else:
                    print("-" * 20)
                    print("No matching posts found on this page.\n")
                    print("-" * 20)
            else:
                print("-" * 20)
                print(f"Failed to fetch page {page_num}. Status code: {response.status_code}\n")
                print("-" * 20)
                break

    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(2)


if __name__ == "__main__":
    renew_connection()  # Tor 네트워크 초기화 및 IP 갱신
    for category in target_categories:
        search_page(target_url=category)
