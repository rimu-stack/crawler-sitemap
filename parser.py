from typing import Any
import requests
from bs4 import BeautifulSoup
import datetime
import time

class ParSite:

    queue : str = []
    visited : str = []

    def __init__(self, site: str) -> None:
        self.site = site
        self.queue = [site]

    def _link_conversion(self, links: list) -> list:
        # for link in self.links:
        #     if link[:1] != 'h':
        #         link = self.site + link
        con_links = sorted([self.site + link if link[:1] != 'h' else link for link in links])
        return [link[:-1] if link[-1:] == '/' else link for link in con_links]
    
    def get_response(self, url: str) -> Any:
        for i in range(10):
            try:
                return requests.get(url, timeout=2.5)
            except Exception as ex:
                print("cannot crawl url {} by reason {}. retry in 1 sec".format(url, ex))
                time.sleep(1)
        return requests.Response()

    def get_all_links(self) -> Any:
        for link in self.queue:
            print(link)
            response = self.get_response(link)
            self.visited.append(link)
            self.queue.remove(link)
            # for line in r.text.split('\n'):
            #     if line.split() == []:
            #         continue

            #     if line.split()[0] == '<a':
            #         print(line.split())
            
            bs = BeautifulSoup(response.text, 'lxml')
            
            links = [str(el.get('href')) for el in bs.find_all('a')]
            
            self.queue.extend([link for link in self._link_conversion(links) if link not in self.visited])
        
        
if __name__ == '__main__':
    startTime = datetime.datetime.now()
    parsing = ParSite('https://crawler-test.com')
    parsing.get_all_links()
    print(datetime.datetime.now() - startTime)
    for link in parsing.visited:
        print(link)