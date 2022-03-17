import re
from urllib.parse import urlparse
import urllib.request
import datetime

class Crawler:

    def __init__(self, site: str) -> None:
        self.site = site
        self.host = urlparse(site).netloc
        self.queue = [site]
        self.visited = []

    def is_iternal(self, link: str) -> bool:
        return urlparse(link).netloc == self.host

    def _link_conversion(self, links: list) -> list:
        conversion_links = []
        for link in links:
            if self.is_iternal(link):
                continue

            link = '%20'.join(link.split())

            check = (link not in conversion_links
                     or link[:-1] not in conversion_links)

            if link.startswith('http:'):
                link = 'https:' + link[5:]
                if check:
                    conversion_links.append(link)
                    continue
            
            if link.startswith('/'):
                link = self.site + link
                conversion_links.append(link)

            if link.endswith('/'):
                link = link[:-1]
                if link.endswith('/'):
                    link = link[:-1]
                    if check:
                        conversion_links.append(link)
                        continue

                if check:
                        conversion_links.append(link)
                        continue

            if link == '#':
                continue

        return conversion_links

    def get_all_links(self) -> None:
        for link in self.queue:
            print('Proccesing ' + link)
            try:
                response = urllib.request.urlopen(link)
            except:
                continue

            if link in self.visited:
                continue

            self.visited.append(link)
            self.queue.remove(link)
        
            page = str(response.read())
            pattern = '<a [^>]*href=[\'|"](.*?)[\'"].*?>'
        
            links = re.findall(pattern, page)
        
            self.queue.extend([link for link in self._link_conversion(links) if link not in self.visited and link not in self.queue and self.is_iternal(link)])


        
    
if __name__ == '__main__':
    startTime = datetime.datetime.now()
    crawler = Crawler('https://crawler-test.com')
    crawler.get_all_links()
    print(datetime.datetime.now() - startTime)
    for link in sorted(crawler.visited):
        print(link)