from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time


def run(db):
    """
    LeakBase 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["leakbase"]  # MongoDB 컬렉션 선택

    # Chrome 옵션 설정
    options = Options()
    options.add_argument("--headless")  # 브라우저 창 표시 없이 실행
    options.add_argument("--disable-blink-features=AutomationControlled")  # Selenium 탐지 방지
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--proxy-server=socks5://127.0.0.1:9050")  # Tor 프록시 설정
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # WebDriver 초기화
    driver = webdriver.Chrome(options=options)

    url = "https://leakbase.io/"
    try:
        driver.get(url)

        # JavaScript 로딩 대기
        time.sleep(5)

        # 페이지 소스 가져오기
        html_content = driver.page_source

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html_content, "html.parser")

        # 게시글 리스트 찾기
        posts = soup.find_all("li", class_="_xgtIstatistik-satir")

        for post in posts:
            try:
                # 게시글 제목
                title_tag = post.find("div", class_="_xgtIstatistik-satir--konu")
                title = title_tag.text.strip() if title_tag else "N/A"

                # 작성자
                author_tag = post.find("div", class_="_xgtIstatistik-satir--hucre _xgtIstatistik-satir--sonYazan")
                author = (
                    author_tag.find("a", class_="username").text.strip()
                    if author_tag and author_tag.find("a", class_="username")
                    else "N/A"
                )

                # 작성 시간
                time_tag = post.find("div", class_="_xgtIstatistik-satir--zaman")
                post_time = time_tag.text.strip() if time_tag else "N/A"

                # 데이터 객체 생성
                post_data = {
                    "title": title,
                    "author": author,
                    "posted_time": post_time,
                    "crawled_time": str(datetime.now()),  # 크롤링 시간 추가
                }

                # 중복 확인 및 데이터 저장
                if not collection.find_one({"title": title}):
                    collection.insert_one(post_data)
                    print(f"데이터 저장 완료: {title}")
                else:
                    print(f"중복 데이터로 저장 건너뜀: {title}")

            except Exception as e:
                print(f"데이터 처리 중 오류 발생: {e}")

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

    finally:
        driver.quit()
