from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient

# MongoDB 설정
client = MongoClient("mongodb://localhost:27017/")
db = client["darkweb"]
collection = db["leakbase"]  # 컬렉션 이름

# Chrome 옵션 설정
options = Options()
options.add_argument("--headless")  # 브라우저 창 표시 없이 실행
options.add_argument("--disable-blink-features=AutomationControlled")  # Selenium 탐지 방지
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--proxy-server=socks5://127.0.0.1:9050")  # Tor 프록시 설정

# "headless"에서 자동화된 속성 비활성화
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# WebDriver 실행
driver = webdriver.Chrome(options=options)
url = "https://leakbase.io/"
driver.get(url)

# JavaScript 실행 대기 (필요에 따라 조정)
time.sleep(5)

# 페이지 소스 가져오기
html_content = driver.page_source

# BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(html_content, "html.parser")

# 게시글 리스트 찾기
posts = soup.find_all("li", class_="_xgtIstatistik-satir")  # 클래스 이름 수정

# 데이터 추출 및 MongoDB 저장
for post in posts:
    try:
        # 게시글 제목
        title_tag = post.find("div", class_="_xgtIstatistik-satir--konu")
        title = title_tag.text.strip() if title_tag else "N/A"

        # 작성자
        author_tag = post.find("div", class_="_xgtIstatistik-satir--hucre _xgtIstatistik-satir--sonYazan")
        author = author_tag.find("a", class_="username").text.strip() if author_tag and author_tag.find("a", class_="username") else "N/A"

        # 작성 시간
        time_tag = post.find("div", class_="_xgtIstatistik-satir--zaman")
        post_time = time_tag.text.strip() if time_tag else "N/A"

        # 데이터 객체 생성
        post_data = {
            "제목": title,
            "작성자": author,
            "작성 시간": post_time
        }

        # 중복 확인 및 데이터 저장
        if not collection.find_one({"제목": title}):
            collection.insert_one(post_data)
            print(f"데이터 저장 완료: {post_data}")
        else:
            print(f"중복 데이터로 저장 건너뜀: {title}")

    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")

# WebDriver 종료
driver.quit()

# MongoDB 연결 종료
client.close()
