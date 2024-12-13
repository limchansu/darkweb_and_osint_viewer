import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from jsonschema import validate, ValidationError

# ChromeDriver 경로
current_dir = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

# TOR 프록시 설정
proxy_address = "127.0.0.1:9050"  # TOR SOCKS5 프록시 주소

# Selenium WebDriver 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")  # TOR 프록시 사용

# WebDriver 초기화
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 크롤링 대상 URL
base_url = "http://3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd.onion"

# JSON Schema 정의
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["title", "description"]
    }
}

def crawl_posts():
    # Selenium으로 페이지 열기
    driver.get(base_url)
    time.sleep(5)  # 페이지 로딩 대기

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.find_all("div", class_="card-body")  # 카드 뉴스 데이터 추출

    results = []

    for card in cards:
        try:
            title = card.find("h5", class_="card-title").text.strip()  # 제목 추출
            description = card.find("p", class_="card-text").text.strip()  # 설명 추출
            post_data = {"title": title, "description": description}

            results.append(post_data)
            print(f"추출 완료: {title}")

        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")

    # JSON Schema 검증
    try:
        validate(instance=results, schema=schema)
        print("데이터 검증 성공!")
    except ValidationError as ve:
        print(f"데이터 검증 실패: {ve}")

    # JSON 파일 저장 (테스트용, 실제 사용 시 반환만 수행)
    # with open("abyss.json", "w", encoding="utf-8") as f:
    #     json.dump(results, f, ensure_ascii=False, indent=4)
    # print("abyss.json 파일 저장 완료.")

    return results

if __name__ == "__main__":
    try:
        data = crawl_posts()
        print(json.dumps(data, ensure_ascii=False, indent=4))  # 결과 출력
    finally:
        # WebDriver 종료
        driver.quit()
