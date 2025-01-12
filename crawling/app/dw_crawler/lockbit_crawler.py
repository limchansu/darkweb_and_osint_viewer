import asyncio

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from .config import TOR_PROXY


async def lockbit(db, show=False):
    collection = db["lockbit"]
    url = "http://lockbit3olp7oetlc4tl5zydnoluphh7fvdt5oa6arcp2757r7xkutid.onion"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, proxy={"server": TOR_PROXY})
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=60000)
            await asyncio.sleep(10)
            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            items = soup.find_all("a", class_="post-block")

            for item in items:
                try:
                    result = {
                        "title": item.find("div", class_="post-title").text.strip(),
                        "content": item.find("div", class_="post-block-text").text.strip(),
                        "post_url": url + item["href"],
                        "update_date": item.find("div", class_="updated-post-date")
                                        .text.strip().replace("\xa0", "").replace("Updated: ", ""),
                    }
                    if show:
                        print(f'lockbit: {result}')
                    if not await collection.find_one({"title": result["title"]}):
                        obj = await collection.insert_one(result)
                        if show:
                            print('lockbit insert success ' + str(obj.inserted_id))

                except Exception as e:
                    print(f"[ERROR] lockbit_crawler.py - lockbit(): {e}")

        except Exception as e:
            print(f"[ERROR] lockbit_crawler.py - lockbit(): {e}")

        finally:
            await browser.close()

