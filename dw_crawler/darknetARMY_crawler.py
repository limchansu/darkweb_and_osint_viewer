from bs4 import BeautifulSoup
import cloudscraper
from datetime import datetime

def scrape_darknetarmy_posts(db, pages=3):
    """
    darknetARMY 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    # MongoDB 컬렉션 선택
    collection = db["darknetARMY"]

    # 크롤러 전용 설정
    base_url = "http://dna777qhcrxy5sbvk7rkdd2phhxbftpdtxvwibih26nr275cdazx4uyd.onion/whats-new/posts/797681/"
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Cloudflare 우회 세션 생성
    scraper = cloudscraper.create_scraper()

    # 페이지 크롤링
    for page in range(1, pages + 1):
        url = f"{base_url}page-{page}"
        print(f"Fetching data for page {page}: {url}")

        # HTML 가져오기
        response = scraper.get(url, proxies=proxies, headers=headers)
        if response.status_code == 200:
            html_content = response.text
        else:
            print(f"Failed to fetch page {page}: {response.status_code}")
            continue

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html_content, 'html.parser')

        # 게시글 목록 추출
        threads = soup.find_all('div', class_='structItem')

        # 게시글 데이터 추출 및 MongoDB 저장
        for thread in threads:
            # 게시글 제목
            title_tag = thread.find('div', class_='structItem-title')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            # 작성자 이름
            author_tag = thread.find('a', class_='username')
            author = author_tag.get_text(strip=True) if author_tag else "N/A"

            # 작성 시간
            time_tag = thread.find('time')
            post_time = time_tag["title"] if time_tag and "title" in time_tag.attrs else "N/A"

            # 데이터 생성
            post_data = {
                "Title": title,
                "Author": author,
                "Posted Time": post_time,
                "Crawled Time": str(datetime.now())
            }

            # 중복 데이터 확인 및 저장
            if not collection.find_one({"Title": title, "Posted Time": post_time}):
                collection.insert_one(post_data)
                print(f"Saved: {post_data}")
            else:
                print(f"Skipped (duplicate): {post_data['Title']}")

        print(f"Page {page} data collection complete.")
        print("-" * 40)
