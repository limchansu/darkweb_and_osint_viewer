from requests_tor import RequestsTor
from bs4 import BeautifulSoup



rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def everest_ransomware_group_crawler():
    results = []
    url = 'http://ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad.onion/page/14'
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
                result['content'] = content.find('p').text.strip().replace('\xa0',' ') if content else ''
                results.append(result)
            older_posts = soup.find("a", class_='next page-numbers')
            if older_posts:
                url = older_posts["href"]
            else:
                url = None

        except Exception as e:
            print(f"everest crawler error: {e}")
    return results