import asyncio
import cloudscraper
from bs4 import BeautifulSoup

def fetch_page_sync(url, proxies, headers):
    """
    동기적으로 페이지 데이터를 가져옵니다.
    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch page {url}: {response.status_code}")
        return None


async def fetch_page(url, proxies, headers):
    """
    `cloudscraper`를 비동기적으로 실행합니다.
    """
    loop = asyncio.get_running_loop()
    # 동기 함수를 비동기적으로 실행
    return await loop.run_in_executor(None, fetch_page_sync, url, proxies, headers)


async def htdark(db):
    """
    비동기 크롤러 실행 및 MongoDB에 데이터 저장
    """
    collection = db["htdark"]
    base_url = "http://ky6urnzorg43zp5sw2gb46csndhpzn6ttpectmeooalwn2zc5w44rbqd.onion"
    proxies = {"http": "socks5h://127.0.0.1:9050"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = base_url + "/index.php?whats-new/posts/5299/"

    while url:
        print(f"Fetching data for page: {url}")
        html_content = await fetch_page(url, proxies, headers)
        if not html_content:
            break

        soup = BeautifulSoup(html_content, 'html.parser')
        threads = soup.find_all('div', class_='structItem')

        for thread in threads:
            title_tag = thread.find('div', class_='structItem-title')
            title = title_tag.get_text(strip=True) if title_tag else None

            author_tag = thread.find('a', class_='username')
            author = author_tag.get_text(strip=True) if author_tag else None

            time_tag = thread.find('li', class_='structItem-startDate')
            post_time = time_tag.get_text(strip=True) if time_tag else None

            post_data = {
                "title": title,
                "author": author,
                "posted Time": post_time,
            }

            if not collection.find_one({"title": title, "posted Time": post_time}):
                collection.insert_one(post_data)
                print(f"Saved: {post_data}")
            else:
                print(f"Skipped (duplicate): {post_data['title']}")

        next_page = soup.find('a', class_='pageNav-jump pageNav-jump--next')
        url = base_url + next_page.get('href') if next_page else None
        print("-" * 40)
