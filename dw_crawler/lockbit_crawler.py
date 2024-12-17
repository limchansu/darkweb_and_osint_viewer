import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.async_api import async_playwright


async def lockbit(db):
    collection = db["lockbit"]
    url = "http://lockbit3olp7oetlc4tl5zydnoluphh7fvdt5oa6arcp2757r7xkutid.onion"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"})
        page = await browser.new_page()

        try:
            print(f"[INFO] 페이지 접근: {url}")
            await page.goto(url, timeout=300000)  # 타임아웃을 5분으로 설정
            await asyncio.sleep(10)

            html_content = await page.content()
            print(html_content)  # 페이지 HTML 내용 출력 (디버깅용)
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
                        "crawled_time": str(datetime.now())
                    }

                    if not await collection.find_one({"title": result["title"]}):
                        await collection.insert_one(result)
                        print(f"Saved: {result['title']}")
                    else:
                        print(f"Skipped (duplicate): {result['title']}")

                except Exception as e:
                    print(f"데이터 처리 중 오류 발생: {e}")

        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")

        finally:
            await browser.close()

