from requests_tor import RequestsTor
from bs4 import BeautifulSoup
from datetime import datetime

# RequestsTor 인스턴스 초기화
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def run(db):
    """
    Daixin 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["daixin"]  # MongoDB 컬렉션 선택
    url = 'http://7ukmkdtyxdkdivtjad57klqnd3kdsmq6tp45rrsxqnu76zzv3jvitlqd.onion/'

    try:
        # Tor 네트워크를 통해 URL 요청
        r = rt.get(url)
        r.raise_for_status()

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all("div", class_='border border-warning card-body shadow-lg')

        for item in items:
            try:
                # 데이터 추출
                result = {}

                # 제목 추출
                title = item.find('h4', class_='border-danger card-title text-start text-white')
                result['title'] = title.text.strip() if title else None

                # 회사 URL 추출
                company_url = item.find('h6', class_='card-subtitle mb-2 text-muted text-start')
                result['company_url'] = (
                    company_url.text.replace('Web Site:', '').strip()
                    if company_url else None
                )

                # 내용 추출
                content = item.find('p', class_='card-text text-start text-white')
                result['content'] = content.text.strip() if content else None

                # 추가 링크 추출
                links = item.find_all('a')
                result['links'] = [link.get('href') for link in links if link.get('href')]

                # 크롤링 시간 추가
                result['crawled_time'] = str(datetime.now())

                # 중복 확인 및 데이터 저장
                if not collection.find_one({"title": result['title'], "company_url": result['company_url']}):
                    collection.insert_one(result)
                    print(f"Saved: {result['title']}")
                else:
                    print(f"Skipped (duplicate): {result['title']}")

            except Exception as e:
                print(f"데이터 추출 중 오류 발생: {e}")

    except Exception as e:
        print(f"daixin crawler error: {e}")
