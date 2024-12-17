import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def leakbase(db):
    collection = db["leakbase"]
    url = "https://leakbase.io/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"})
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector("li._xgtIstatistik-satir")

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            posts = soup.find_all("li", class_="_xgtIstatistik-satir")

            for post in posts:
                title_tag = post.find("div", class_="_xgtIstatistik-satir--konu")
                title = title_tag.text.strip() if title_tag else None

                author_tag = post.find("div", class_="_xgtIstatistik-satir--hucre _xgtIstatistik-satir--sonYazan")
                author = author_tag.find("a", class_="username").text.strip() if author_tag and author_tag.find("a") else None

                time_tag = post.find("div", class_="_xgtIstatistik-satir--zaman")
                post_time = time_tag.text.strip() if time_tag else None

                post_data = {
                    "title": title,
                    "author": author,
                    "posted_time": post_time,
                }

                if title and not await collection.find_one({"title": title}):
                    print(post_data)
                    print(await collection.insert_one(post_data))

        except Exception as e:
            print(f"[ERROR] leakbase_crawler.py - leakbase(): {e}")
        finally:
            await browser.close()



