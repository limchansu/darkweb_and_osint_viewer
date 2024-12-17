import asyncio
from concurrent.futures import ThreadPoolExecutor
from requests_tor import RequestsTor
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

# RequestsTor 인스턴스 초기화
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def crawl_blacksuit_page(url, collection):
    """
    BlackSuit 개별 페이지를 크롤링하는 동기 함수
    """
    try:
        # 메인 페이지 요청 및 파싱
        r = rt.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        # 페이지 번호 가져오기
        page_numbers = [a.text.strip() for a in soup.select('.pagination a')]

        for page_number in page_numbers:
            page_url = f'{url}?page={page_number}'
            page_response = rt.get(page_url)
            page_soup = BeautifulSoup(page_response.text, 'html.parser')

            # 게시글 정보 추출
            items = page_soup.find_all("div", class_='card')
            for item in items:
                result = {}

                # 제목
                title = item.find('div', class_='title')
                result['title'] = title.text.strip() if title else None
                result['post_url'] = url + title.find('a').get('href') if title else ''

                # 회사 정보
                try:
                    company = item.find('div', class_='url').find('a')
                    result['company'] = company['href'] if company else ''
                except Exception:
                    result['company'] = ''

                # 내용
                content = item.find('div', class_='text')
                result['content'] = content.text.strip() if content else None

                # 추가 링크
                links = []
                link_div = item.find('div', class_='links')
                if link_div:
                    link_tags = link_div.find_all('a')
                    links = [link.get('href') for link in link_tags if link.get('href')]
                result['links'] = links

                # 크롤링 시간 추가
                result['Crawled Time'] = str(datetime.now())

                # 중복 확인 및 데이터 저장
                if not collection.find_one({"title": result['title'], "post_url": result['post_url']}):
                    collection.insert_one(result)

    except Exception as e:
        print(f"[ERROR] blacksuit_crawler.py - crawl_blacksuit_page(): {e}")


async def blackbasta(db):
    """
    BlackSuit 크롤러 실행 및 MongoDB 컬렉션에 비동기적 저장
    """
    collection = db["blacksuit"]
    base_url = 'http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/'

    # ThreadPoolExecutor를 사용해 비동기적으로 동기 함수 실행
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, crawl_blacksuit_page, base_url, collection)

if __name__ == "__main__":
    # MongoDB 연결 설정
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(blackbasta(db))
