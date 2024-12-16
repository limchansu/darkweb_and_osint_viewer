from requests_tor import RequestsTor
from bs4 import BeautifulSoup
from datetime import datetime

# RequestsTor 인스턴스 초기화
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def run(db):
    """
    BlackSuit 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["blacksuit"]  # MongoDB 컬렉션 선택
    url = 'http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/'

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
                except:
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
                    print(f"Saved: {result['title']}")
                else:
                    print(f"Skipped (duplicate): {result['title']}")

    except Exception as e:
        print(f"blacksuit crawler error : {e}")
