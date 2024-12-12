from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time, pprint


# Selenium Tor 프록시 설정
options = Options()
options.add_argument("--proxy-server=socks5://127.0.0.1:9050")  # Tor 프록시 설정
options.add_argument("--headless")  # 브라우저를 표시하지 않음
options.add_argument("--disable-gpu")  # GPU 비활성화
options.add_argument("--no-sandbox")  # 샌드박스 비활성화 (Linux 환경에서 필수)

service = Service('./chromedriver')  # chromedriver 경로 설정
driver = webdriver.Chrome(service=service, options=options)

def lockbit_crawler():
    results = []
    url = 'http://lockbit3olp7oetlc4tl5zydnoluphh7fvdt5oa6arcp2757r7xkutid.onion'
    driver.get(url)

    # 페이지가 로드될 때까지 대기
    time.sleep(10)  # 필요 시 WebDriverWait로 대체

    # BeautifulSoup로 HTML 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.find_all('a', class_='post-block')
    for item in items:
        result = {}
        result['title'] = item.find('div', class_='post-title').text.strip()
        result['content'] = item.find('div', class_='post-block-text').text.strip()
        result['post_url'] = item['href']
        print(result)
        results.append(result)
    driver.quit()  # 브라우저 종료
    return results


lockbit_crawler()