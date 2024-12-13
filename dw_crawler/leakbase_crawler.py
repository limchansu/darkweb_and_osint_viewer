from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Selenium 및 Proxy 설정
PROXY = "127.0.0.1:9050"  # Tor 프록시 주소
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")  # 브라우저 창 표시 없이 실행
CHROME_OPTIONS.add_argument("--disable-blink-features=AutomationControlled")  # Selenium 탐지 방지
CHROME_OPTIONS.add_argument("--disable-gpu")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_argument(f"--proxy-server=socks5://{PROXY}")  # Tor 프록시 설정
CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])
CHROME_OPTIONS.add_experimental_option("useAutomationExtension", False)

def scrape_leakbase_posts(url):
    # WebDriver 실행
    driver = webdriver.Chrome(options=CHROME_OPTIONS)
    driver.get(url)

    # JavaScript 실행 대기
    time.sleep(5)

    # 페이지 소스 가져오기
    html_content = driver.page_source

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(html_content, "html.parser")

    # 게시글 리스트 찾기
    posts = soup.find_all("li", class_="_xgtIstatistik-satir")

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
            "Title": title,           
            "Author": author,         
            "Posted Time": post_time  
        })

    # WebDriver 종료
    driver.quit()

    return data_list

url = "https://leakbase.io/"
result = scrape_leakbase_posts(url)

# 결과 출력
for data in result:
    print(data)

