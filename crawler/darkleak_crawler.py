import os
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from stem.control import Controller
from stem import SocketError

# TOR 설정
TOR_EXECUTABLE_PATH = r".\tor.exe"  # TOR 실행 파일 경로
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

# 크롬 드라이버 설정
chrome_driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
chrome_service = Service(chrome_driver_path)

# Selenium 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://127.0.0.1:{TOR_SOCKS_PORT}")

# 크롤링 대상 URL
base_url = "http://darkleakyqmv62eweqwy4dnhaijg4m4dkburo73pzuqfdumcntqdokyd.onion/index.html"

# 데이터 저장용 리스트
all_data = []

# 크롤링 함수
def crawl_files():
    renew_tor_ip()  # TOR IP 갱신

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(base_url)
    rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")

    for row in rows:
        try:
            file_name = row.find_element(By.CSS_SELECTOR, "td a strong").text.strip()

            # 크롤링 데이터 저장
            file_data = {"file_name": file_name}
            all_data.append(file_data)

            print(f"수집 완료: {file_name}")
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")

    # JSON 파일로 저장
    with open("darkleaky_files.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("darkleaky_files.json 파일 저장 완료.")
    driver.quit()

if __name__ == "__main__":
    try:
        start_tor()  # TOR 실행
        crawl_files()
    except Exception as e:
        print(f"스크립트 실행 중 오류 발생: {e}")
