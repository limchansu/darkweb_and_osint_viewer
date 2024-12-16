from requests_tor import RequestsTor
from bs4 import BeautifulSoup

rt = RequestsTor(tor_ports=(9050,), tor_cport=9051)

def play_cralwer():
    results = []
    url = 'http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion/'
    r = rt.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    pages = soup.find_all('span', class_='Page')
    pages = int(pages[-1].text)
    for page in range(1, pages+1):
        page_url = f'{url}index.php?page={page}'
        r = rt.get(page_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('th', class_='News')
        for item in items:
            post_url = f'{url}topic.php?id={item['onclick'].split('\'')[1]}'
            r = rt.get(post_url)
            result = {
                'title':'',
                'update_date':'',
                'content':'',
                'links':[],
                'rar_password':''
                      }
            soup = BeautifulSoup(r.text, 'html.parser')
            info = soup.find('th')
            temp = info.find('div').text.split('\xa0')
            result['title'] = temp[0]
            info = info.find('div').text
            start = info.find('added: ')
            end = info.find('publication date: ')
            result['update_date'] = info[start + len('added: ') : end] if start != -1 and end != -1 else ''
            start = info.find('information: ')
            end = info.find('DOWNLOAD LINKS: ')
            end = len(info) if end == -1 else end
            result['content'] = info[start : end] if start != -1 and end != -1 else ''

            start = end + len('DOWNLOAD LINKS: ')
            password = info.find('Rar password: ')
            end = password if password != -1 else len(info)
            if start != -1 and end != -1:
                links = info[start:end].split('http')
                for link in links:
                    if len(link) > 0:
                        link = link.replace(':', 'http:')
                        result['links'].append(link)
                start = end + len('Rar password: ')
            result['rar_password'] = info[start:].strip() if password != -1 else ''
            results.append(result)
    return results
