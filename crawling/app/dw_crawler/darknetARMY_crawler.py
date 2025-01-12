import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup

from .config import TOR_PROXY


async def fetch_page(session, url):

    try:
        async with session.get(url, timeout=30) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"[ERROR] darknetARMY_crawler.py - fetch_page(): {e}")
        return None

async def process_page(db, session, base_url, show):

    collection = db["darknetARMY"]
    url = 'http://dna777qhcrxy5sbvk7rkdd2phhxbftpdtxvwibih26nr275cdazx4uyd.onion/whats-new/posts/804733/'

    while True:
        html_content = await fetch_page(session, url)
        if not html_content:
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        threads = soup.find_all('div', class_='structItem')
        if not threads:
            print("[INFO] No threads found on this page.")
            break

        for thread in threads:
            title_tag = thread.find('div', class_='structItem-title')
            title = title_tag.get_text(strip=True) if title_tag else None

            author_tag = thread.find('a', class_='username')
            author = author_tag.get_text(strip=True) if author_tag else None

            time_tag = thread.find('time')
            post_time = time_tag["title"] if time_tag and "title" in time_tag.attrs else None

            post_data = {
                "title": title,
                "author": author,
                "posted Time": post_time,
            }
            if show:
                print(f'darknetARMY: {post_data}')
            if title and not await collection.find_one({"title": title, "posted Time": post_time}):
                obj = await collection.insert_one(post_data)
                if show:
                    print('darknetARMY insert success ' + str(obj.inserted_id))

        page = soup.find('a', class_='pageNav-jump pageNav-jump--next')
        if page and 'href' in page.attrs:
            url = base_url + page['href']
        else:
            break

async def darknetARMY(db, show=False):

    base_url = "http://dna777qhcrxy5sbvk7rkdd2phhxbftpdtxvwibih26nr275cdazx4uyd.onion/"

    connector = ProxyConnector.from_url(TOR_PROXY)
    headers = {"User-Agent": "Mozilla/5.0"}

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        await process_page(db, session, base_url, show)