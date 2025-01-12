# 사이트 닫힘.....

from bs4 import BeautifulSoup
from requests_tor import RequestsTor

# RequestsTor 초기화
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def run(db):
    """
    Everest Ransomware Group 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["everest"]  # MongoDB 컬렉션 선택
    base_url = 'http://ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad.onion/'

    url = base_url  # 초기 URL
    while url:
        try:
            # 페이지 요청 및 BeautifulSoup 파싱
            r = rt.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')

            # 게시글 정보 추출
            items = soup.find_all('article')
            for item in items:
                try:
                    result = {}

                    # 제목과 게시글 URL 추출
                    title = item.find('h2', class_='entry-title heading-size-1')
                    result['title'] = title.text.strip() if title else None
                    result['post_url'] = title.find('a').get('href') if title and title.find('a') else None

                    # 내용 추출
                    content = item.find('div', class_='entry-content')
                    result['content'] = content.find('p').text.strip().replace('\xa0', ' ') if content and content.find('p') else None




                    # 중복 확인 및 데이터 저장
                    if not collection.find_one({"title": result['title'], "post_url": result['post_url']}):
                        collection.insert_one(result)
                        print(f"Saved: {result['title']}")
                    else:
                        print(f"Skipped (duplicate): {result['title']}")

                except Exception as e:
                    print(f"데이터 추출 중 오류 발생: {e}")

            # 다음 페이지 URL 확인
            older_posts = soup.find("a", class_='next page-numbers')
            url = older_posts["href"] if older_posts else None

        except Exception as e:
            print(f"Everest crawler error: {e}")
            break
