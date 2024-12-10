from requests_tor import RequestsTor
from bs4 import BeautifulSoup
import pprint


# 프록시 포트를 9050으로 설정
rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def show_ip() :
    url = 'http://icanhazip.com/'
    r = rt.get(url)
    print(r.text)

def daixin_crawler():
    results = []  # 결과를 저장할 리스트
    url = 'http://7ukmkdtyxdkdivtjad57klqnd3kdsmq6tp45rrsxqnu76zzv3jvitlqd.onion/'  # 대상 URL

    try:
        r = rt.get(url)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'html.parser')

        items = soup.find_all("div", class_='border border-warning card-body shadow-lg')

        for item in items:
            result = {}
            title = item.find('h4', class_='border-danger card-title text-start text-white')
            result['title'] = title.text.strip() if title else None
            company_url = item.find('h6', class_='card-subtitle mb-2 text-muted text-start')
            company_url = company_url.text if company_url else None
            company_url = company_url.replace('Web Site:', '').strip()
            result['company_url'] = company_url
            content = item.find('p', class_='card-text text-start text-white')
            result['content'] = content.text.strip() if content else None
            links = item.find_all('a')
            result['links'] = [link.get('href') for link in links if link.get('href')]
            results.append(result)
    except Exception as e:
        print(f"An error occurred: {e}")

    return results



def blacksuit_crawler():
    url = 'http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/'
    results = []

    try:
        r = rt.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        page_numbers = [a.text.strip() for a in soup.select('.pagination a')]

        for page_number in page_numbers:
            page_url = f'{url}?page={page_number}'
            page_response = rt.get(page_url)
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            items = page_soup.find_all("div", class_='card')

            for item in items:
                result = {}
                title = item.find('div', class_='title')
                result['title'] = title.text.strip() if title else None
                result['post_url'] = url + title.find('a').get('href') if title else ''
                try:
                    company = item.find('div', class_='url').find('a')
                    result['company'] = company['href'] if company else ''
                except:
                    result['company'] = ''

                content = item.find('div', class_='text')
                result['content'] = content.text.strip() if content else None

                links = []
                link_div = item.find('div', class_='links')
                if link_div:
                    link_tags = link_div.find_all('a')
                    links = [link.get('href') for link in link_tags if link.get('href')]
                result['links'] = links

                results.append(result)
    except Exception as e:
        print(f"An error occurred: {e}")
    return results

def everest_ransomware_group_crwaler():
    results = []
    url = 'http://ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad.onion/'
    while url:

        try:
            r = rt.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.find_all('article')
            for item in items:
                result = {}
                title = item.find('h2', class_='entry-title heading-size-1')
                result['title'] = title.text.strip() if title else ''
                result['post_url'] = title.find('a').get('href') if title else ''
                content = item.find('div', class_='entry-content')
                result['content'] = content.find('p').text.strip() if content else ''
                results.append(result)
            older_posts = soup.find("a", string="Older Posts")

            if older_posts and older_posts.get("href"):
                url = older_posts["href"]
            else:
                url = None

        except Exception as e:
            print(f"An error occurred: {e}")
    return results

