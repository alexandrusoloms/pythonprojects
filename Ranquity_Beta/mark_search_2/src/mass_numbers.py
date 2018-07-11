import os 
import requests
from bs4 import BeautifulSoup
from Get_Numbers import NumberCollector
from urllib.parse import urlparse

base_url = input('Provide base url: ')
base_base = urlparse(base_url)[1]

response = requests.get(base_url, timeout = 10)
html = response.content
response.close()
soup = BeautifulSoup(html, 'lxml')

link_list = []
link_list.append(base_url)
for tag in soup.findAll('a'):
    try:
        link_list.append(tag.get('href'))
    except:
        pass

done_links = []
for c, link in enumerate(link_list):
    if link not in done_links:
        try: 
            NumberCollector.numbered_sentences(url=link)
        except:
            try:
                link = 'http://' + base_base + link
            except:
                pass
    else:
        print('Already done')
    done_links.append(link)
    print('{}/{} done'.format(c, len(link_list)))
