import asyncio
import playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime
from fake_useragent import UserAgent

schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "description": {"type": "string"},
        "crawled_time": {"type": "string", "format": "date-time"},
    },
    "required": ["title", "url", "description"],
}

async def blackbasta(db, show=False):
    collection = db["blackbasta"]
    ua = UserAgent()
    random_user_agent = ua.random
    base_url = "http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion"
    category_url = f"{base_url}/"

    proxy_address = "127.0.0.1:9050"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, proxy={
            "server": f"socks5://{proxy_address}"
        })
        context = await browser.new_context(user_agent=random_user_agent)
        page = await context.new_page()

        try:
            await page.goto(category_url, timeout=60000)
            await asyncio.sleep(10)
            while True:
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                posts = soup.find_all("div", class_="title")
                for post in posts:
                    try:
                        title_element = post.find("a", class_="blog_name_link")
                        if not title_element:
                            continue

                        title = title_element.text.strip()
                        url = title_element["href"].strip()

                        # Description 추출
                        description_element = post.find_next("p", {"data-v-md-line": "3"})
                        description = (
                            description_element.get_text(strip=True)
                            if description_element
                            else ""
                        )

                        post_data = {
                            "title": title,
                            "url": url,
                            "description": description,
                            "crawled_time": str(datetime.now()),
                        }

                        try:
                            validate(instance=post_data, schema=schema)
                            if show:
                                print(f'blackbasta: {post_data}')
                            if not await collection.find_one({"title": title, "url": url}):
                                obj = await collection.insert_one(post_data)
                                if show:
                                    print('blackbasta insert success ' + str(obj.inserted_id))

                        except ValidationError as e:
                            print(f"[ERROR] blackbasta_crawler - blackbasta: {e.message}")

                    except Exception as e:
                        print(f"[ERROR] blackbasta_crawler - blackbasta: {e}")
                next_button = page.locator('div.next-page-btn')
                if next_button:
                    try:
                        await next_button.click(timeout=10000)
                        await asyncio.sleep(10)
                    except playwright.async_api.TimeoutError as e:
                        return
                else:
                    break
        except Exception as e:
            print(f"[ERROR] blackbasta_crawler - blackbasta: {e}")
        finally:
            await browser.close()

