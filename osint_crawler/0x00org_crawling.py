import requests
from bs4 import BeautifulSoup
import json
import socks
import socket
from stem import Signal
from stem.control import Controller
import time
import random
import re

# Tor 네트워크를 재시작하여 새로운 IP 할당
def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='cert0188!')  # 비밀번호 설정 (torrc 파일에서 설정하지 않았다면 빈 문자열)
        controller.signal(Signal.NEWNYM)
        print("New Tor connection requested.")

# Tor 프록시를 통한 요청 함수
def tor_request(url, headers=None):
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    time.sleep(random.uniform(3, 8))
    response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
    return response

# 키워드 로드 함수
def load_keywords(file_path):
    """Load keywords from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get("keywords", [])
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {file_path}.")
        return []

# 포스트 제목 및 URL 가져오기
def fetch_post_titles(base_url):
    """Fetch post titles and URLs from the given base URL."""
    try:
        response = tor_request(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all post titles and URLs
        posts = []
        for link in soup.find_all('a', class_='title raw-link raw-topic-link', href=True):
            title = link.get_text(strip=True)
            url = link['href']  # Use the href directly without appending base_url
            posts.append((title, url))
        return posts
    except requests.RequestException as e:
        print(f"Error fetching URL {base_url}: {e}")
        return []

# 포스트 내용 가져오기
def fetch_post_content(url):
    """Fetch the content of a specific post."""
    try:
        response = tor_request(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text(strip=True)
        return content
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""

# 제목에서 키워드 매칭 확인
def match_keywords_in_titles(posts, keywords):
    """Check if keywords are present in the fetched post titles."""
    results = []
    for title, url in posts:
        matched_keywords = []
        for keyword in keywords:
            # 공백을 포함한 키워드 처리 (하이픈과 밑줄 대체)
            keyword_pattern = re.escape(keyword).replace(" ", "[-_]")
            # 단어 경계를 포함한 정규식 생성
            pattern = rf'\b{keyword_pattern}\b'
            # 제목에서 키워드 패턴 찾기
            if re.search(pattern, title, re.IGNORECASE):  # 대소문자 구분 없이 매칭
                matched_keywords.append(keyword)
        if matched_keywords:  # 한 개 이상의 키워드가 매칭된 경우
            # 키워드를 쉼표로 구분된 문자열로 저장
            results.append({
                "url": url,
                "keywords": ", ".join(matched_keywords),  # 쉼표로 구분된 문자열
                "title": title
            })
    return results

# 키워드 카운트로 포스트 필터링
def filter_posts_by_keyword_count(results, keywords):
    """Filter posts where the keyword appears at least 3 times in the content."""
    filtered_results = []
    for url, keyword, title in results:
        content = fetch_post_content(url)
        if content.lower().count(keyword.lower()) >= 3:
            filtered_results.append({"url": url, "keyword": keyword, "title": title})
    return filtered_results

# 결과 저장
def save_results(results, file_path):
    """Save the results to a JSON file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(results, file, indent=4)
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")

# 메인 함수
def main():
    start_time = time.time()
    keywords_file = "cleaned_keywords.json"
    result_file = "resultt.json"
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

    # Load keywords from JSON file
    keywords = load_keywords(keywords_file)
    if not keywords:
        print("No keywords found. Exiting.")
        return

    all_results = []

    # Fetch post titles and URLs for all base URLs
    for base_url in base_urls:
        print(f"Fetching post titles and URLs from {base_url}...")
        posts = fetch_post_titles(base_url)

        if not posts:
            print(f"No posts found for {base_url}. Continuing.")
            continue

        # Match keywords in titles
        print("Matching keywords in titles...")
        results = match_keywords_in_titles(posts, keywords)
        all_results.extend(results)

    if not all_results:
        print("No matching posts found.")
        return

    # Filter posts by keyword count in content
    print("Filtering posts by keyword count in content...")
    filtered_results = filter_posts_by_keyword_count(all_results, keywords)

    if not filtered_results:
        print("No posts with sufficient keyword matches found.")
        return

    # Save results to a file
    print(f"Saving results to {result_file}...")
    save_results(filtered_results, result_file)
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes = elapsed_time
    print(f"Done. Total time taken: {elapsed_minutes:.2f} minutes.")

if __name__ == "__main__":
    renew_connection()  # Tor 네트워크 초기화 및 IP 갱신
    main()

