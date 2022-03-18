from concurrent.futures import ThreadPoolExecutor
import re
from urllib.parse import urlparse, urlsplit, urlunsplit
import urllib.request
import datetime

class Crawler:

    def __init__(self, site: str, threads=None) -> None:
        self.site = site
        self.scheme = urlparse(site).scheme
        self.netloc = urlparse(site).netloc
        self.queue = [site]
        self.visited = []
        self.threads = threads

    def is_iternal(self, link: str) -> bool:
        return urlparse(link).netloc == self.netloc

    def _link_conversion(self, links: list) -> list:
        conversion_links = []
        for link in links:
            if link == '/' or link == '#':
                continue

            url = urlsplit(link)

            if url.query:
                if all([not url.netloc, not url.path]):
                    url = url._replace(scheme=self.scheme,
                                       netloc=self.netloc,
                                       path='/')

            url = url._replace(scheme=self.scheme)
            
            if not url.netloc:
                url = url._replace(netloc=self.netloc)
    
            new_path = url.path
            new_path = '%20'.join(new_path.strip('/').split())
            new_path = '%5C'.join(new_path.split('\\'))

            url = url._replace(path=new_path)
            
            link = urlunsplit(url)

            if not self.is_iternal(link):
                continue

            check = link not in conversion_links

            if link.endswith('/'):
                link = link[:-1]
                        
            if check:
                conversion_links.append(link)
                continue

        return conversion_links

    def _read_link(self, link: str) -> None:
        link = self.queue[0]
        self.queue.pop(0)

        print('Processing ' + link)

        try:
            response = urllib.request.urlopen(link)
        except:
            return

        if link in self.visited:
            return

        self.visited.append(link)

        page = str(response.read())
        pattern = '<a [^>]*href=[\'|"](.*?)[\'"].*?>'
    
        links = re.findall(pattern, page)
        
        links = self._link_conversion(links)

        if not links:
            return
         
        self.queue.extend([link for link in links if link not in self.visited and link not in self.queue])

    def get_all_links(self) -> None:
        if self.threads:
            self._read_link(self.site)

            with ThreadPoolExecutor(self.threads) as excecutor:
                try:
                    excecutor.map(self._read_link, self.queue, timeout=3)
                except KeyboardInterrupt:
                    exit()
        else:
            while self.queue:
                self._read_link(self.queue[0])

        
    
if __name__ == '__main__':
    startTime = datetime.datetime.now()
    crawler = Crawler('https://crawler-test.com')
    crawler.get_all_links()
    print(datetime.datetime.now() - startTime)
    for link in sorted(crawler.visited):
        print(link)