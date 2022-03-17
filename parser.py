from concurrent.futures import ThreadPoolExecutor
import re
from urllib.parse import urlparse
import urllib.request
import datetime

class Crawler:

    def __init__(self, site: str, threads: int = 6) -> None:
        self.site = site
        self.host = urlparse(site).netloc
        self.queue = [site]
        self.visited = []
        self.threads = threads

    def is_iternal(self, link: str) -> bool:
        return urlparse(link).netloc == self.host

    def _link_conversion(self, links: list) -> list:
        conversion_links = []
        for link in links:
            if self.is_iternal(link):
                continue
            
            if link in self.queue:
                continue
            
            if link.startswith('?'):
                continue

            if link == '#':
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
                if check:
                        conversion_links.append(link)
                        continue

        return conversion_links

    def _read_link(self, link: str) -> None:
        print('Processing ' + link)
        try:
            response = urllib.request.urlopen(link)
        except:
            return

        if link in self.visited:
            return

        self.visited.append(link)
        self.queue.remove(link)

        page = str(response.read())
        pattern = '<a [^>]*href=[\'|"](.*?)[\'"].*?>'
    
        links = re.findall(pattern, page)
    
        self.queue.extend([link for link in self._link_conversion(links) if link not in self.visited and link not in self.queue and self.is_iternal(link)])

    def get_all_links(self) -> None:
        self._read_link(self.site)
        with ThreadPoolExecutor(200) as excecutor:
            try:
                excecutor.map(self._read_link, self.queue, timeout=3)
            except KeyboardInterrupt:
                exit()


        
    
if __name__ == '__main__':
    startTime = datetime.datetime.now()
    crawler = Crawler('https://crawler-test.com')
    crawler.get_all_links()
    print(datetime.datetime.now() - startTime)
    for link in sorted(crawler.visited):
        print(link)