from requests_tor import RequestsTor
from bs4 import BeautifulSoup
from datetime import datetime

# Tor Requests 설정
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def run(db):
    """
    Rhysida 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["rhysida"]  # MongoDB 컬렉션 선택
    url = 'http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/archive.php'

    try:
        # 페이지 요청 및 HTML 파싱
        r = rt.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # 데이터 추출
        items = soup.find_all('div', class_="col-10")
        for item in items:
            try:
                # 게시글 정보 추출
                title = item.find('div', class_='m-2 h4').text.strip()
                content = item.select_one('div.m-2:not(.h4)').text.strip()
                links = [link['href'] for link in item.find_all('a', href=True)] or []

                # 데이터 생성
                post_data = {
                    "title": title,
                    "content": content,
                    "links": links,
                    "crawled_time": str(datetime.now())  # 크롤링 시간 추가
                }

                # 중복 확인 및 데이터 저장
                if not collection.find_one({"title": title}):
                    collection.insert_one(post_data)
                    print(f"Saved: {title}")
                else:
                    print(f"Skipped (duplicate): {title}")

            except Exception as e:
                print(f"데이터 처리 중 오류 발생: {e}")

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
