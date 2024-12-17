import os
import asyncio
from datetime import datetime
from jsonschema import validate, ValidationError
from pymongo import MongoClient
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# JSON Schema 정의
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

async def crawl_page(category_url, proxy_address, schema, collection):
    """
    개별 페이지를 비동기적으로 크롤링하는 함수 (Playwright 사용)
    """
    try:
        async with async_playwright() as p:
            # Proxy와 User-Agent를 설정한 브라우저 context 생성
            browser = await p.chromium.launch(headless=True, proxy={
                "server": f"socks5://{proxy_address}"
            })
            context = await browser.new_context(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            ))

            page = await context.new_page()
            print(f"[INFO] Navigating to {category_url}...")
            await page.goto(category_url, timeout=120000)

            # 페이지 로딩 완료 대기
            try:
                await page.wait_for_selector(".title", timeout=60000)
                print("[INFO] .title selector found.")
            except Exception:
                print("[WARNING] .title selector not found. Check the page structure.")

            # 페이지 내용 출력 (디버깅)
            content = await page.content()
            print(f"[DEBUG] Page content length: {len(content)}")

            # BeautifulSoup으로 HTML 파싱
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

                    # 데이터 생성
                    post_data = {
                        "title": title,
                        "url": url,
                        "description": description,
                        "crawled_time": str(datetime.now()),
                    }

                    # JSON Schema 검증
                    try:
                        validate(instance=post_data, schema=schema)

                        # 중복 확인 및 데이터 저장
                        if not collection.find_one({"title": title, "url": url}):
                            collection.insert_one(post_data)
                            print(f"Saved: {title}")

                    except ValidationError as e:
                        print(f"[ERROR] blackbasta_crawler.py - crawl_page(): {e.message}")

                except Exception as e:
                    print(f"[ERROR] blackbasta_crawler.py - crawl_page(): {e}")

            await browser.close()

    except Exception as e:
        print(f"[ERROR] blackbasta_crawler.py - crawl_page(): {e}")

async def blackbasta(db):
    """
    BlackBasta 크롤러 실행 및 MongoDB 컬렉션에 비동기적 저장
    """
    collection = db["blackbasta"]  # MongoDB 컬렉션 선택
    proxy_address = "127.0.0.1:9050"

    # 크롤링 대상 URL
    base_url = "http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion"
    category_url = f"{base_url}/"

    # 비동기 실행
    tasks = [crawl_page(category_url, proxy_address, schema, collection)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # MongoDB 연결 설정
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(blackbasta(db))
