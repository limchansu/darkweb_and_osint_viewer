from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
import chardet
from .config import TOR_PROXY


async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=ClientTimeout(total=60)) as response:
            response.raise_for_status()
            content = await response.read()
            detected_encoding = chardet.detect(content)['encoding']
            if not detected_encoding:
                detected_encoding = 'utf-8'
            return content.decode(detected_encoding, errors='ignore')
    except Exception as e:
        print(f"[ERROR] rhysida_crawler.py - fetch_page(): {e}")
        return None


async def rhysida(db, show=False):
    collection = db["rhysida"]
    url = 'http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/archive.php'

    connector = ProxyConnector.from_url(TOR_PROXY)

    async with ClientSession(connector=connector) as session:
        html = await fetch_page(session, url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_="col-10")

        for item in items:
            try:
                title = item.find('div', class_='m-2 h4').text.strip()
                content = item.select_one('div.m-2:not(.h4)').text.strip()
                links = [link['href'] for link in item.find_all('a', href=True)] or []

                post_data = {
                    "title": title,
                    "content": content,
                    "links": links,
                }
                if show:
                    print(f'rhysida: {post_data}')
                if not await collection.find_one({"title": title}):
                    obj = await collection.insert_one(post_data)
                    if show:
                        print('rhysida insert success ' + str(obj.inserted_id))

            except Exception as e:
                print(f"[ERROR] rhysida_crawler.py - rhysida(): {e}")

