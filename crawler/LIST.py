from types import NoneType

from requests_tor import RequestsTor
from bs4 import BeautifulSoup

# 프록시 포트를 9050으로 설정
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)


def daixin_crawler() :
    url = 'http://7ukmkdtyxdkdivtjad57klqnd3kdsmq6tp45rrsxqnu76zzv3jvitlqd.onion/'

    r = rt.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')

    items = soup.find_all("div", class_='border border-warning card-body shadow-lg')

    for item in items:
        # 제목 처리
        title = item.find('h4', class_='border-danger card-title text-start text-white')
        print(f"Title: {title.text.strip() if title else '내용이 없습니다.'}")
        print()
        # 회사 이름 처리
        company = item.find('h6', class_='card-subtitle mb-2 text-muted text-start')
        print(f"Company: {company.text.strip() if company else '내용이 없습니다.'}")
        print()
        # 내용 처리
        content = item.find('p', class_='card-text text-start text-white')
        print(f"Content: {content.text.strip() if content else '내용이 없습니다.'}")
        print()

        # 링크 처리
        links = item.find_all('a')
        if links:
            for link in links:
                print(f"Link: {link.text.strip()} ({link.get('href')})")
        else:
            print("Links: 내용이 없습니다.")
        print()


