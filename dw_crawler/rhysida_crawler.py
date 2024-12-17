import asyncio
from aiohttp_socks import ProxyConnector
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from datetime import datetime
import chardet



async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=ClientTimeout(total=60)) as response:
            response.raise_for_status()
            # 바이너리 데이터 수신
            content = await response.read()
            # 인코딩 자동 감지
            detected_encoding = chardet.detect(content)['encoding']
            if not detected_encoding:
                detected_encoding = 'utf-8'  # 감지 실패 시 기본값
            return content.decode(detected_encoding, errors='ignore')  # 인코딩 후 디코딩
    except Exception as e:
        print(f"[ERROR] 페이지 요청 실패 ({url}): {e}")
        return None


async def rhysida(db):
    collection = db["rhysida"]
    url = 'http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/archive.php'
    proxy = "socks5://127.0.0.1:9050"

    # SOCKS5 프록시 설정
    connector = ProxyConnector.from_url(proxy)

    async with ClientSession(connector=connector) as session:
        print(f"[INFO] 페이지 접근: {url}")
        html = await fetch_page(session, url)
        if not html:
            print("[ERROR] 페이지를 가져오지 못했습니다.")
            return

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_="col-10")

        for item in items:
            try:
                title = item.find('div', class_='m-2 h4').text.strip()
                content = item.select_one('div.m-2:not(.h4)').text.strip()
                links = [link['href'] for link in item.find_all('a', href=True)] or []

                post_data = {
                    "title": title,
                    "content": content,
                    "links": links,
                    "crawled_time": str(datetime.now())
                }

                if not await collection.find_one({"title": title}):
                    await collection.insert_one(post_data)
                    print(f"Saved: {title}")
                else:
                    print(f"Skipped (duplicate): {title}")

            except Exception as e:
                print(f"[ERROR] 데이터 처리 중 오류 발생: {e}")

