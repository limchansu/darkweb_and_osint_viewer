from bs4 import BeautifulSoup
import cloudscraper

def scrape_htdark_posts(base_url, proxies, headers, pages=10):
    # Cloudflare 우회 세션 생성
    scraper = cloudscraper.create_scraper()
    all_threads = []

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

        # 게시글 데이터 추출
        for thread in threads:
            # 게시글 제목
            title_tag = thread.find('div', class_='structItem-title')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            # 작성자 이름
            author_tag = thread.find('a', class_='username')
            author = author_tag.get_text(strip=True) if author_tag else "N/A"

            # 작성 시간
            time_tag = thread.find('li', class_='structItem-startDate')
            post_time = time_tag.get_text(strip=True) if time_tag else "N/A"

            # 게시글 데이터 저장
            all_threads.append({
                "Title": title,
                "Author": author,
                "Posted Time": post_time
            })

        print(f"Page {page} data collection complete.")
        print("-" * 40)

    return all_threads


base_url = "http://ky6urnzorg43zp5sw2gb46csndhpzn6ttpectmeooalwn2zc5w44rbqd.onion/index.php?whats-new/posts/4878/"
proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 크롤링 실행
scraped_data = scrape_htdark_posts(base_url, proxies, headers, pages=10)

# 결과 출력
for data in scraped_data:
    print(data)
