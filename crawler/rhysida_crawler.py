from requests_tor import RequestsTor
from bs4 import BeautifulSoup
import pprint



rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def rhysida_crawler():
    results = []
    url = 'http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion/archive.php'
    r = rt.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.find_all('div', class_="col-10")
    for item in items:
        result = {}
        result['title'] = item.find('div', class_='m-2 h4').text
        result['content'] = item.select_one('div.m-2:not(.h4)').text.strip()
        urls = [link['href'] for link in item.find_all('a', href=True)]
        result['urls'] = urls if urls else ''
        results.append(result)

    return results

pprint.pprint(rhysida_crawler())