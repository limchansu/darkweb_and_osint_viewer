import asyncio
from aiohttp_socks import ProxyConnector
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# Tor 프록시 설정
TOR_PROXY = "socks5://127.0.0.1:9050"

async def fetch_page(session, url):
    """
    비동기적으로 페이지를 요청하는 함수
    """
    try:
        async with session.get(url, timeout=30) as response:
            response.raise_for_status()
            print(f"[INFO] 페이지 가져오기 성공: {url}")
            return await response.text()
    except Exception as e:
        print(f"[ERROR] 페이지 요청 실패: {url} - {e}")
        return None

async def process_page(db, html):
    """
    HTML 데이터를 파싱하고 MongoDB에 저장하는 함수
    """
    collection = db["daixin"]  # MongoDB 컬렉션 선택
    try:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all("div", class_='border border-warning card-body shadow-lg')

        for item in items:
            try:
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
                print(f"[ERROR] 데이터 추출 중 오류 발생: {e}")
    except Exception as e:
        print(f"[ERROR] HTML 파싱 중 오류 발생: {e}")

async def daixin(db):
    """
    Daixin 크롤러 비동기 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    url = 'http://7ukmkdtyxdkdivtjad57klqnd3kdsmq6tp45rrsxqnu76zzv3jvitlqd.onion/'
    connector = ProxyConnector.from_url(TOR_PROXY)

    async with ClientSession(connector=connector) as session:
        print("[INFO] Daixin 크롤러 실행 시작...")
        html = await fetch_page(session, url)

        if html:
            await process_page(db, html)

    print("[INFO] Daixin 크롤러 실행 완료")

if __name__ == "__main__":
    # MongoDB 연결 설정
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(daixin(db))
