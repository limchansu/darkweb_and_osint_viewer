import os
import subprocess
import json
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from stem.control import Controller
from stem import SocketError
from selenium.webdriver.common.proxy import Proxy, ProxyType

# TOR 설정
TOR_EXECUTABLE_PATH = r"C:\Program Files (x86)\Tor\tor.exe"  # TOR 실행 파일 경로
TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051

# TOR 실행 함수
def start_tor():
    if not os.path.exists(TOR_EXECUTABLE_PATH):
        raise FileNotFoundError("TOR 실행 파일이 없습니다. 경로를 확인하세요.")
    subprocess.Popen([TOR_EXECUTABLE_PATH])
    print("TOR 실행 중...")

# TOR IP 갱신 함수
def renew_tor_ip():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate()  # 인증 필요 시 비밀번호 전달
            controller.signal("NEWNYM")  # 새 IP 요청
            print("TOR IP 갱신 완료.")
    except SocketError as e:
        print(f"TOR 연결 실패: {e}")
        raise

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017/")  # 로컬 MongoDB URI
db = client["CrackingIslandDB"]  # 데이터베이스 이름
collection = db["Combolists"]  # 컬렉션 이름

# 크롬 드라이버 설정
chrome_driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
chrome_service = Service(chrome_driver_path)

# 프록시 설정
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = f"127.0.0.1:{TOR_SOCKS_PORT}"
proxy.ssl_proxy = f"127.0.0.1:{TOR_SOCKS_PORT}"

# Selenium 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

# 크롤링 대상 URL
base_url = "https://crackingisland.net"
category_url = f"{base_url}/categories/combolists"

# 데이터 저장용 리스트
all_data = []

# 크롤링 함수
def crawl_combolists():
    renew_tor_ip()  # TOR IP 갱신

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(category_url)
    posts = driver.find_elements(By.CSS_SELECTOR, 'a[itemprop="url"]')

    for post in posts:
        try:
            title = post.find_element(By.CSS_SELECTOR, 'h2[itemprop="headline"]').text.strip()
            post_url = base_url + post.get_attribute("href")
            post_type = post.find_element(By.CSS_SELECTOR, 'span[itemprop="about"]').text.strip()
            post_date = post.find_element(By.CSS_SELECTOR, 'span[itemprop="dateCreated"]').text.strip()
            description = post.find_element(By.CSS_SELECTOR, 'p[itemprop="text"]').text.strip()

            # MongoDB 저장 데이터
            post_data = {
                "title": title,
                "url": post_url,
                "type": post_type,
                "dateCreated": post_date,
                "description": description,
            }

            # MongoDB 저장
            collection.update_one(
                {"url": post_url},  # 중복 방지를 위한 기준
                {"$set": post_data},
                upsert=True  # 기존 데이터가 없으면 삽입
            )
            print(f"저장 완료: {title}")

            # JSON 파일 저장용 데이터 추가
            all_data.append(post_data)

        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")

    # JSON 파일로 저장
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("test.json 파일 저장 완료.")
    driver.quit()

if __name__ == "__main__":
    try:
        start_tor()  # TOR 실행
        crawl_combolists()
    except Exception as e:
        print(f"스크립트 실행 중 오류 발생: {e}")
