import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup



async def fetch_page(session, url):

    try:
        async with session.get(url, timeout=30) as response:
            return await response.text()
    except Exception as e:
        print(f"[ERROR] blacksuit_crawler.py - fetch_page(): {e}")
        return None


async def blacksuit(db, show=False):

    url = 'http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/'
    connector = ProxyConnector.from_url("socks5://tor:9050")
    collection = db['blacksuit']
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            html = await fetch_page(session, url)
            if not html:
                return

            soup = BeautifulSoup(html, 'html.parser')
            page_numbers = [a.text.strip() for a in soup.select('.pagination a')]

            for page_number in page_numbers:
                page_url = f'{url}?page={page_number}'
                page_html = await fetch_page(session, page_url)
                if not page_html:
                    continue
                page_soup = BeautifulSoup(page_html, 'html.parser')

                items = page_soup.find_all("div", class_='card')
                for item in items:
                    result = {}

                    title = item.find('div', class_='title')
                    result['title'] = title.text.strip() if title else None
                    result['post_url'] = url + title.find('a').get('href') if title else ''

                    company = item.find('div', class_='url').find('a') if item.find('div', class_='url') else None
                    result['company'] = company['href'] if company else ''

                    content = item.find('div', class_='text')
                    result['content'] = content.text.strip() if content else None

                    links = []
                    link_div = item.find('div', class_='links')
                    if link_div:
                        link_tags = link_div.find_all('a')
                        links = [link.get('href') for link in link_tags if link.get('href')]
                    result['links'] = links
                    if show:
                        print(f'blacksuit: {result}')
                    if not await collection.find_one({"title": result['title'], "post_url": result['post_url']}):
                        obj = await collection.insert_one(result)
                        if show:
                            print('blacksuit insert success ' + str(obj.inserted_id))

        except Exception as e:
            print(f"[ERROR] blacksuit_crawler.py - crawl_blacksuit_page(): {e}")


