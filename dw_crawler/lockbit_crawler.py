from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time


def run(db):
    """
    LockBit 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["lockbit"]  # MongoDB 컬렉션 선택

    # Selenium Tor 프록시 설정
    options = Options()
    options.add_argument("--proxy-server=socks5://127.0.0.1:9050")  # Tor 프록시 설정
    options.add_argument("--headless")  # 브라우저를 표시하지 않음
    options.add_argument("--disable-gpu")  # GPU 비활성화
    options.add_argument("--no-sandbox")  # 샌드박스 비활성화 (Linux 환경에서 필수)

    driver = webdriver.Chrome(options=options)

    url = 'http://lockbit3olp7oetlc4tl5zydnoluphh7fvdt5oa6arcp2757r7xkutid.onion'

    try:
        driver.get(url)

        # 페이지 로드 대기
        time.sleep(10)

        # BeautifulSoup로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('a', class_='post-block')

        for item in items:
            try:
                # 데이터 추출
                result = {
                    "title": item.find('div', class_='post-title').text.strip(),
                    "content": item.find('div', class_='post-block-text').text.strip(),
                    "post_url": url + item['href'],
                    "update_date": item.find('div', class_='updated-post-date').text.strip().replace('\xa0', '').replace('Updated: ', ''),
                    "crawled_time": str(datetime.now())  # 크롤링 시간 추가
                }

                # 중복 확인 및 데이터 저장
                if not collection.find_one({"title": result["title"]}):
                    collection.insert_one(result)
                    print(f"Saved: {result['title']}")
                else:
                    print(f"Skipped (duplicate): {result['title']}")

            except Exception as e:
                print(f"데이터 처리 중 오류 발생: {e}")

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

    finally:
        driver.quit()  # 브라우저 종료
