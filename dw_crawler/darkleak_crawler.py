import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError
from datetime import datetime

def run(db):
    """
    DarkLeak 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    # MongoDB 컬렉션 선택
    collection = db["darkleak"]

    # 크롤링 대상 URL
    base_url = "http://darkleakyqmv62eweqwy4dnhaijg4m4dkburo73pzuqfdumcntqdokyd.onion"
    category_url = f"{base_url}/index.html"

    # ChromeDriver 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

    # Selenium WebDriver 옵션 설정
    proxy_address = "127.0.0.1:9050"  # TOR SOCKS5 프록시 주소
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")

    # WebDriver 초기화
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Selenium으로 페이지 열기
        driver.get(category_url)
        driver.implicitly_wait(5)  # 페이지 로딩 대기

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.find_all("tr", onclick=True)  # 클릭 가능한 행 추출

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
                schema = {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string"},
                        "url": {"type": ["string", "null"]},
                        "crawled_time": {"type": "string"}
                    },
                    "required": ["file_name", "url"]
                }
                validate(instance=post_data, schema=schema)

                # 중복 확인 및 데이터 저장
                if not collection.find_one({"file_name": file_name, "url": full_url}):
                    collection.insert_one(post_data)
                    print(f"Saved: {file_name}, URL: {full_url}")
                else:
                    print(f"Skipped (duplicate): {file_name}")

            except ValidationError as e:
                print(f"데이터 검증 실패: {e.message}")
            except Exception as e:
                print(f"데이터 추출 중 오류 발생: {e}")

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

    finally:
        driver.quit()
