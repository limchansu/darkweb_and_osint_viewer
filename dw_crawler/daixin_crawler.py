from requests_tor import RequestsTor
from bs4 import BeautifulSoup



rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def daixin_crawler():
    results = []
    url = 'http://7ukmkdtyxdkdivtjad57klqnd3kdsmq6tp45rrsxqnu76zzv3jvitlqd.onion/'

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
        print(f"daixin crawler error : {e}")

    return results




