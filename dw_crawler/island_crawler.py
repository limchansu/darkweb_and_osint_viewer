import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime

def run(db):
    """
    Island 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["island"]  # MongoDB 컬렉션 선택

    # 크롤링 대상 URL (onion 사이트)
    base_url = "https://crackingisland.net/"  # onion 사이트 URL로 변경 필요 시 업데이트
    category_url = f"{base_url}/categories/combolists"



    # Selenium WebDriver 옵션 설정
    proxy_address = "127.0.0.1:9050"  # TOR SOCKS5 프록시 주소
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")

    # WebDriver 초기화
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Selenium으로 페이지 열기
        driver.get(category_url)
        time.sleep(5)  # JavaScript 로딩 대기

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.find_all("a", itemprop="url")

        for post in posts:
            try:
                # 데이터 추출
                title = post.find("h2", itemprop="headline").text.strip()
                post_url = base_url + post["href"]
                post_type = post.find("span", itemprop="about").text.strip()
                post_date = post.find("span", itemprop="dateCreated").text.strip()
                description = post.find("p", itemprop="text").text.strip()

                # 데이터 생성
                post_data = {
                    "title": title,
                    "url": post_url,
                    "type": post_type,
                    "dateCreated": post_date,
                    "description": description,
                    "crawled_time": str(datetime.now()),  # 크롤링 시간 추가
                }

                # JSON Schema 검증
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

                try:
                    validate(instance=post_data, schema=schema)

                    # 중복 확인 및 데이터 저장
                    if not collection.find_one({"title": title, "url": post_url}):
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
