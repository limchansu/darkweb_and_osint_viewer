import asyncio
import cloudscraper
from bs4 import BeautifulSoup
from .config import TOR_PROXYh

def fetch_page_sync(url, proxies, headers):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None


async def fetch_page(url, proxies, headers):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_page_sync, url, proxies, headers)


async def htdark(db, show=False):
    collection = db["htdark"]
    base_url = "http://ky6urnzorg43zp5sw2gb46csndhpzn6ttpectmeooalwn2zc5w44rbqd.onion"
    proxies = {"http": TOR_PROXYh}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = base_url + "/index.php?whats-new/posts/5299/"

    while url:
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
            if show:
                print(f'htdark: {post_data}')
            if not await collection.find_one({"title": title, "posted Time": post_time}):
                obj = await collection.insert_one(post_data)
                if show:
                    print('htdark insert success ' + str(obj.inserted_id))

        next_page = soup.find('a', class_='pageNav-jump pageNav-jump--next')
        url = base_url + next_page.get('href') if next_page else None