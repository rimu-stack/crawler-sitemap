import requests
from bs4 import BeautifulSoup
import datetime

class ParSite:

    links : str = []

    def __init__(self, site: str) -> None:
        self.site = site

    def _link_conversion(self):
        # for link in self.links:
        #     if link[:1] != 'h':
        #         link = self.site + link
        self.links = [self.site + link if link[:1] != 'h' else link for link in self.links]
        self.links = sorted(self.links)
        self.links = [link[:-1] if link[-1:] == '/' else link for link in self.links]

    def get_href(self):
        r = requests.get(self.site)

        # for line in r.text.split('\n'):
        #     if line.split() == []:
        #         continue

        #     if line.split()[0] == '<a':
        #         print(line.split())
        
        bs = BeautifulSoup(r.text, 'lxml')
        
        self.links = [str(el.get('href')) for el in bs.find_all('a')]
        self._link_conversion()
        self.links = set(self.links)
        
        
if __name__ == '__main__':
    startTime = datetime.datetime.now()
    parsing = ParSite('https://crawler-test.com')
    parsing.get_href()
    print(datetime.datetime.now() - startTime)
    for link in parsing.links:
        print(link)