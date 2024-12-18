import asyncio
from aiohttp_socks import ProxyConnector
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pymongo import MongoClient
from .config import TOR_PROXY

async def fetch_page(session, url):

    try:
        async with session.get(url, timeout=30) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"[ERROR] daixin_crawler.py - fetch_page(): {e}")
        return None

async def process_page(db, html, show):

    collection = db["daixin"]
    try:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all("div", class_='border border-warning card-body shadow-lg')

        for item in items:
            try:
                result = {}

                title = item.find('h4', class_='border-danger card-title text-start text-white')
                result['title'] = title.text.strip() if title else None

                company_url = item.find('h6', class_='card-subtitle mb-2 text-muted text-start')
                result['company_url'] = (
                    company_url.text.replace('Web Site:', '').strip()
                    if company_url else None
                )


                content = item.find('p', class_='card-text text-start text-white')
                result['content'] = content.text.strip() if content else None

                links = item.find_all('a')
                result['links'] = [link.get('href') for link in links if link.get('href')]

                if show:
                    print(f'daixin: {result}')

                if not await collection.find_one({"title": result['title'], "company_url": result['company_url']}):
                    obj = await collection.insert_one(result)
                    if show:
                        print('daixin insert success ' + str(obj.inserted_id))

            except Exception as e:
                print(f"[ERROR] daixin_crawler.py - process_page(): {e}")
    except Exception as e:
        print(f"[ERROR] daixin_crawler.py - process_page(): {e}")

async def daixin(db, show=False):

    url = 'http://7ukmkdtyxdkdivtjad57klqnd3kdsmq6tp45rrsxqnu76zzv3jvitlqd.onion/'
    connector = ProxyConnector.from_url(TOR_PROXY)

    async with ClientSession(connector=connector) as session:
        html = await fetch_page(session, url)

        if html:
            await process_page(db, html, show)

