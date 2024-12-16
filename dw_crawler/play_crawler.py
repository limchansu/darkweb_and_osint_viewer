from requests_tor import RequestsTor
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB 설정
client = MongoClient("mongodb://localhost:27017/")
db = client["darkweb"]
collection = db["play"]

# Tor Requests 설정
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def play_crawler():
    url = 'http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion/'
    r = rt.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # 페이지 수 확인
    pages = soup.find_all('span', class_='Page')
    pages = int(pages[-1].text) if pages else 1

    # 페이지 순회
    for page in range(1, pages + 1):
        page_url = f'{url}index.php?page={page}'
        r = rt.get(page_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('th', class_='News')

        for item in items:
            try:
                # onclick 속성에서 ID 추출
                onclick_content = item['onclick']
                post_id = onclick_content.split("'")[1]
                post_url = f"{url}topic.php?id={post_id}"

                # 상세 페이지 요청
                r = rt.get(post_url)
                result = {
                    'title': '',
                    'update_date': '',
                    'content': '',
                    'links': [],
                    'rar_password': ''
                }

                soup = BeautifulSoup(r.text, 'html.parser')
                info = soup.find('th')

                # 제목 추출
                temp = info.find('div').text.split('\xa0')
                result['title'] = temp[0]

                # 추가 정보 파싱
                info_text = info.find('div').text
                start = info_text.find('added: ')
                end = info_text.find('publication date: ')
                result['update_date'] = info_text[start + len('added: '): end].strip() if start != -1 and end != -1 else ''

                start = info_text.find('information: ')
                end = info_text.find('DOWNLOAD LINKS: ')
                result['content'] = info_text[start + len('information: '): end].strip() if start != -1 and end != -1 else ''

                # 다운로드 링크 및 RAR 비밀번호 추출
                start = info_text.find('DOWNLOAD LINKS: ') + len('DOWNLOAD LINKS: ')
                password_index = info_text.find('Rar password: ')
                end = password_index if password_index != -1 else len(info_text)
                
                if start != -1 and end != -1:
                    links = info_text[start:end].split('http')
                    for link in links:
                        if len(link.strip()) > 0:
                            result['links'].append(f"http{link.strip()}")

                # RAR 비밀번호 추출
                result['rar_password'] = info_text[password_index + len('Rar password: '):].strip() if password_index != -1 else ''

                # 중복 확인 및 MongoDB에 데이터 저장
                if not collection.find_one({"title": result['title']}):
                    collection.insert_one(result)
                    print(f"데이터 저장 완료: {result}")
                else:
                    print(f"중복 데이터로 저장 건너뜀: {result['title']}")

            except Exception as e:
                print(f"데이터 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    try:
        play_crawler()
    finally:
        client.close()  # MongoDB 연결 종료
