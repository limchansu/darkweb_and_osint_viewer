from requests_tor import RequestsTor
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB 설정
client = MongoClient("mongodb://localhost:27017/")
db = client["darkweb"]
collection = db["rhysida"]

# Tor Requests 설정
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def rhysida_crawler():
    url = 'http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/archive.php'
    r = rt.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.find_all('div', class_="col-10")
    
    for item in items:
        try:
            # 데이터 추출
            result = {
                'title': item.find('div', class_='m-2 h4').text.strip(),
                'content': item.select_one('div.m-2:not(.h4)').text.strip(),
                'links': [link['href'] for link in item.find_all('a', href=True)] or ''
            }

            # 중복 확인 및 데이터 저장
            if not collection.find_one({"title": result['title']}):
                collection.insert_one(result)
                print(f"데이터 저장 완료: {result}")
            else:
                print(f"중복 데이터로 저장 건너뜀: {result['title']}")

        except Exception as e:
            print(f"데이터 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    try:
        rhysida_crawler()
    finally:
        client.close()  # MongoDB 연결 종료
