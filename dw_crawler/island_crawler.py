import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from jsonschema import validate, ValidationError

async def island(db):
    """
    Playwright를 사용해 Island 사이트 크롤링 및 MongoDB에 비동기 저장
    """
    collection = db["island"]

    # 크롤링 대상 URL 및 프록시 설정
    base_url = "https://crackingisland.net"
    category_url = f"{base_url}/categories/combolists"
    proxy_address = "socks5://127.0.0.1:9050"

    # JSON Schema 설정
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
            # 페이지 열기
            print(f"[INFO] 페이지 접근: {category_url}")
            await page.goto(category_url, timeout=60000)
            await asyncio.sleep(5)  # 페이지 로딩 대기

            while True:  # Next 버튼을 눌러가며 계속 반복
                # HTML 파싱
                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                posts = soup.find_all("a", itemprop="url")

                # 게시글 데이터 처리
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
                            "crawled_time": str(datetime.now()),
                        }
                        print(post_data)
                        # JSON Schema 검증
                        validate(instance=post_data, schema=schema)

                        # 중복 확인 및 저장
                        if not await collection.find_one({"title": title, "url": post_url}):
                            await collection.insert_one(post_data)
                            print(f"Saved: {title}")
                        else:
                            print(f"Skipped (duplicate): {title}")

                    except ValidationError as ve:
                        print(f"[ERROR] 데이터 검증 실패: {ve.message}")
                    except Exception as e:
                        print(f"[ERROR] 데이터 처리 중 오류 발생: {e}")

                # Next 버튼 클릭 시도
                next_button = await page.query_selector('li.pagination_linkText__cuIa8 >> text="Next"')
                if next_button:
                    print("[INFO] Next 버튼 클릭")
                    await next_button.click()
                    await asyncio.sleep(3)  # 페이지 로딩 대기
                else:
                    print("[INFO] 더 이상 Next 버튼이 없습니다. 크롤링 완료.")
                    break

        except Exception as e:
            print(f"[ERROR] 크롤링 중 오류 발생: {e}")

        finally:
            await browser.close()