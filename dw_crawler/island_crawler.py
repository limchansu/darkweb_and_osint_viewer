import asyncio

import playwright
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from jsonschema import validate

async def island(db, show=False):
    collection = db["island"]
    base_url = "https://crackingisland.net"
    category_url = f"{base_url}/categories/combolists"
    proxy_address = "socks5://127.0.0.1:9050"

    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "url": {"type": "string"},
            "type": {"type": "string"},
            "dateCreated": {"type": "string"},
            "description": {"type": "string"},
            "crawled_time": {"type": "string"},
        },
        "required": ["title", "url", "type", "dateCreated", "description"],
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(proxy={"server": proxy_address})
        page = await context.new_page()

        try:
            await page.goto(category_url, timeout=60000)
            await asyncio.sleep(5)

            while True:
                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                posts = soup.find_all("a", itemprop="url")

                for post in posts:
                    try:
                        title = post.find("h2", itemprop="headline").text.strip()
                        post_url = base_url + post["href"]
                        post_type = post.find("span", itemprop="about").text.strip()
                        post_date = post.find("span", itemprop="dateCreated").text.strip()
                        description = post.find("p", itemprop="text")
                        description = description.text.strip() if description else ''

                        post_data = {
                            "title": title,
                            "url": post_url,
                            "type": post_type,
                            "dateCreated": post_date,
                            "description": description,
                        }

                        validate(instance=post_data, schema=schema)
                        if show:
                            print(f'island: {post_data}')
                        if not await collection.find_one({"title": title, "url": post_url}):
                            obj = await collection.insert_one(post_data)
                            if show:
                                print('island insert success ' + str(obj.inserted_id))

                    except Exception as e:
                        print(f"[ERROR] island_crawler.py - island(): {e}")

                next_button = await page.query_selector('li.pagination_linkText__cuIa8 >> text="Next"')
                print(next_button)
                if next_button:
                    try:
                        await next_button.click(timeout=3000)
                    except playwright.async_api.TimeoutError as e:
                        return
                    await asyncio.sleep(3)
                else:
                    break

        except Exception as e:
            print(f"[ERROR] island_crawler.py - island(): {e}")

        finally:
            await browser.close()

