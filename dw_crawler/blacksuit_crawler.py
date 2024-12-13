from requests_tor import RequestsTor
from bs4 import BeautifulSoup



rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

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
        print(f"blacksuit crawler error : {e}")
    return results