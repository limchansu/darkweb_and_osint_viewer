import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
from jsonschema import validate, ValidationError

def run(db):
    """
    Abyss 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["abyss"]  # MongoDB 컬렉션 선택

    # ChromeDriver 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

    # Selenium WebDriver 옵션 설정
    proxy_address = "127.0.0.1:9050"  # TOR SOCKS5 프록시 주소
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창 표시 없이 실행
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")

    # WebDriver 초기화
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 크롤링 대상 URL
    base_url = "http://3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd.onion"

    # JSON Schema 정의
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "crawled_time": {"type": "string"}
        },
        "required": ["title", "description"]
    }

    try:
        # Selenium으로 페이지 열기
        driver.get(base_url)
        driver.implicitly_wait(5)  # 페이지 로딩 대기

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.find_all("div", class_="card-body")  # 카드 데이터 추출

        for card in cards:
            try:
                # 데이터 추출
                title = card.find("h5", class_="card-title").text.strip()
                description = card.find("p", class_="card-text").text.strip()

                # 데이터 생성
                post_data = {
                    "title": title,
                    "description": description,
                    "crawled_time": str(datetime.now())
                }

                # JSON Schema 검증
                try:
                    validate(instance=post_data, schema=schema)

                    # 중복 확인 및 데이터 저장
                    if not collection.find_one({"title": title, "description": description}):
                        collection.insert_one(post_data)
                        print(f"Saved: {title}")
                    else:
                        print(f"Skipped (duplicate): {title}")

                except ValidationError as ve:
                    print(f"데이터 검증 실패: {ve.message}")

            except Exception as e:
                print(f"데이터 추출 중 오류 발생: {e}")

    except Exception as e:
        print(f"Abyss 크롤링 중 오류 발생: {e}")

    finally:
        driver.quit()
