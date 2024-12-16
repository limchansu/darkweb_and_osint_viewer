import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime

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

def run(db):
    """
    BlackBasta 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    # MongoDB 컬렉션 선택
    collection = db["blackbasta"]

    # 크롤링 대상 URL
    base_url = "http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion"
    category_url = f"{base_url}/"

    # ChromeDriver 경로 설정
#    current_dir = os.path.dirname(os.path.abspath(__file__))
#    chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

    # Selenium WebDriver 옵션 설정
    proxy_address = "127.0.0.1:9050"  # Tor SOCKS5 프록시 주소
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    # WebDriver 초기화
#    service = Service(chromedriver_path)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Selenium으로 페이지 열기
        driver.get(category_url)

        # JavaScript 로딩 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "title"))
        )

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
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
                    else:
                        print(f"Skipped (duplicate): {title}")

                except ValidationError as e:
                    print(f"데이터 검증 실패: {e.message}")

            except Exception as e:
                print(f"데이터 추출 중 오류 발생: {e}")

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

    finally:
        driver.quit()
