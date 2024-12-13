import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError

# ChromeDriver 경로 (프로젝트 폴더 내에 위치한 chromedriver.exe)
current_dir = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(current_dir, "chromedriver.exe")

# Tor 프록시 설정
proxy_address = "127.0.0.1:9050"  # Tor SOCKS5 프록시 주소

# Selenium WebDriver 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")  # Tor 프록시 사용
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)

# WebDriver 초기화
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 크롤링 대상 URL
base_url = "http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion"
category_url = f"{base_url}/"

# JSON Schema 정의
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "description": {"type": "string"},
    },
    "required": ["title", "url", "description"],
}

# 크롤링 함수
def crawl_blackbasta():
    all_data = []
    try:
        # Selenium으로 페이지 열기
        driver.get(category_url)

        # JavaScript 로딩 대기 (명시적으로 요소가 로드될 때까지 대기)
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

                # Description 추출 (p 태그에서 data-v-md-line="3"만 선택)
                description_element = post.find_next("p", {"data-v-md-line": "3"})
                description = (
                    description_element.get_text(strip=True)
                    if description_element
                    else ""
                )

                # 데이터 저장
                post_data = {
                    "title": title,
                    "url": url,
                    "description": description,
                }

                # JSON Schema 검증
                try:
                    validate(instance=post_data, schema=schema)
                    all_data.append(post_data)
                    print(f"추출 완료: {title}")
                except ValidationError as e:
                    print(f"데이터 검증 실패: {e.message}")

            except Exception as e:
                print(f"데이터 추출 중 오류 발생: {e}")

        # JSON 파일로 저장 (주석 처리)
        # with open("blackbasta.json", "w", encoding="utf-8") as f:
        #     json.dump(all_data, f, ensure_ascii=False, indent=4)
        # print("blackbasta.json 파일 저장 완료.")

        return all_data

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return []

    finally:
        driver.quit()


if __name__ == "__main__":
    result = crawl_blackbasta()
    print(result)
