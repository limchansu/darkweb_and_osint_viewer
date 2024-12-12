from bs4 import BeautifulSoup
import cloudscraper


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
# Tor 프록시 설정
proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}


# Cloudflare 우회 세션 생성
scraper = cloudscraper.create_scraper()

# 기본 URL (페이지 번호 제외)
base_url = "http://dna777qhcrxy5sbvk7rkdd2phhxbftpdtxvwibih26nr275cdazx4uyd.onion/whats-new/posts/788219/"

# 게시글 데이터를 저장할 리스트
all_threads = []

# 페이지 크롤링
for page in range(1, 3):  # 예: 1~5 페이지까지 크롤링
    url = f"{base_url}page-{page}"  # 동적으로 URL 생성
    print(f"페이지 {page} 데이터 가져오는 중: {url}")
    
    # HTML 가져오기
    response = scraper.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"페이지 {page} 요청 실패: {response.status_code}")
        continue

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 게시글 목록 추출
    threads = soup.find_all('div', class_='structItem')

    # 게시글 데이터 추출
    for thread in threads:
        # 게시글 제목
        title_tag = thread.find('div', class_='structItem-title')
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        # 작성자 이름
        author_tag = thread.find('a', class_='username')
        author = author_tag.get_text(strip=True) if author_tag else "N/A"

        # 작성 시간
        time_tag = thread.find('time', class_='structItem-latestDate u-dt')
        time = time_tag.get_text(strip=True) if time_tag else "N/A"

        # 게시글 데이터 저장
        all_threads.append({
            "제목": title,
            "작성자": author,
            "작성 시간": time
        })

    print(f"페이지 {page} 데이터 수집 완료")
    print("-" * 40)

# 결과 출력
for thread in all_threads:
    print(f"제목: {thread['제목']}, 작성자: {thread['작성자']}, 작성 시간: {thread['작성 시간']}")

# 선택: 결과를 파일에 저장 (JSON 형식)
import json
with open("DarknetARMY.json", "w", encoding="utf-8") as f:
    json.dump(all_threads, f, ensure_ascii=False, indent=4)
