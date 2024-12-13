from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import time


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

# 데이터 추출
data_list = []
for post in posts:
    # 게시글 제목
    title_tag = post.find("div", class_="_xgtIstatistik-satir--konu")
    title = title_tag.text.strip() if title_tag else "N/A"

    # 작성자
    author_tag = post.find("div", class_="_xgtIstatistik-satir--hucre _xgtIstatistik-satir--sonYazan")
    author = author_tag.find("a", class_="username").text.strip() if author_tag and author_tag.find("a", class_="username") else "N/A"

    # 작성 시간
    time_tag = post.find("div", class_="_xgtIstatistik-satir--zaman")
    post_time = time_tag.text.strip() if time_tag else "N/A"

    # 데이터 저장
    data_list.append({
        "제목": title,
        "작성자": author,
        "작성 시간": post_time
    })

# WebDriver 종료
driver.quit()

# 결과 출력
for data in data_list:
    print(f"제목: {data['제목']}, 작성자: {data['작성자']}, 작성 시간: {data['작성 시간']}")

# 결과를 파일에 저장 (JSON 형식)
import json
with open("leakbase_posts.json", "w", encoding="utf-8") as f:
    json.dump(data_list, f, ensure_ascii=False, indent=4)
