import os
import asyncio
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient  # 비동기 MongoDB 클라이언트

# JSON Schema 정의
SCHEMA = {
    "type": "object",
    "properties": {
        "file_name": {"type": "string"},
        "url": {"type": ["string", "null"]},
        "crawled_time": {"type": "string"}
    },
    "required": ["file_name", "url"]
}

# TOR Proxy 설정
TOR_PROXY = "socks5://127.0.0.1:9050"

async def fetch_page(driver, url):
    """
    Selenium으로 페이지를 가져오는 비동기 함수
    """
    print(f"[INFO] 페이지 로드: {url}")
    try:
        driver.get(url)
        await asyncio.sleep(3)  # 페이지 로드 대기
        return driver.page_source
    except Exception as e:
        print(f"[ERROR] 페이지 로드 실패: {e}")
        return None

async def process_page(db, html, base_url):
    """
    HTML을 파싱하고 데이터를 MongoDB에 저장하는 함수
    """
    collection = db["darkleak"]
    try:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr", onclick=True)

        for row in rows:
            try:
                # 파일 이름 추출
                file_name = row.find("strong").text.strip()

                # onclick 속성에서 URL 추출
                onclick_attr = row.get("onclick")
                if onclick_attr and "window.location='" in onclick_attr:
                    relative_url = onclick_attr.split("'")[1]
                    full_url = f"{base_url}/{relative_url}"
                else:
                    full_url = None

                # 데이터 생성
                post_data = {
                    "file_name": file_name,
                    "url": full_url,
                    "crawled_time": str(datetime.now())
                }

                # JSON Schema 검증
                validate(instance=post_data, schema=SCHEMA)

                # 중복 확인 및 데이터 저장
                if not await collection.find_one({"file_name": file_name, "url": full_url}):
                    await collection.insert_one(post_data)
                    print(f"Saved: {file_name}, URL: {full_url}")
                else:
                    print(f"Skipped (duplicate): {file_name}")

            except ValidationError as e:
                print(f"[ERROR] 데이터 검증 실패: {e.message}")
            except Exception as e:
                print(f"[ERROR] 데이터 처리 중 오류: {e}")

    except Exception as e:
        print(f"[ERROR] HTML 파싱 중 오류 발생: {e}")

async def darkleak(db):
    """
    DarkLeak 크롤러 실행 (비동기)
    """
    base_url = "http://darkleakyqmv62eweqwy4dnhaijg4m4dkburo73pzuqfdumcntqdokyd.onion"
    category_url = f"{base_url}/index.html"

    # ChromeDriver 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server={TOR_PROXY}")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 페이지 가져오기
        html = await fetch_page(driver, category_url)
        if html:
            # 페이지 처리 및 데이터 저장
            await process_page(db, html, base_url)
    except Exception as e:
        print(f"[ERROR] 크롤링 중 오류 발생: {e}")
    finally:
        driver.quit()
        print("[INFO] 드라이버 종료")

if __name__ == "__main__":
    # 비동기 MongoDB 연결
    MONGO_URI = "mongodb://localhost:27017"
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(darkleak(db))
