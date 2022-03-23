import re
import threading
from urllib.error import HTTPError
from urllib.parse import urlparse, urlsplit, urlunsplit, quote
import urllib.request
import time
from socket import timeout


class Crawler:
    def __init__(self, site: str, threads=None) -> None:
        self.site = site
        self.scheme = urlparse(site).scheme
        self.netloc = urlparse(site).netloc
        self.visited = []
        self.queue = [site]
        self.threads = threads if threads else 1
        self.not_response = []

    def is_iternal(self, link: str) -> bool:
        return urlparse(link).netloc == self.netloc

    def _link_conversion(self, links: list) -> list:
        conversion_links = []
        for link in links:
            if len(link) < 2:
                continue

            url = urlsplit(link)

            if url.path:
                new_path = re.sub(r'//+', '/', quote(url.path.encode('utf8')))

            if not url.path:
                new_path = ''

            if url.query or url.fragment:
                if all([not url.netloc, not url.path]):
                    new_path = '/'

            if url.netloc:
                new_netloc = url.netloc

            if any([not url.netloc, url.netloc == self.netloc]):
                new_netloc = self.netloc

            if url.scheme:
                new_scheme = url.scheme
                if new_scheme not in ['http', 'https']:
                    continue
            
            if not url.scheme:
                new_scheme = self.scheme
                
            url = url._replace(scheme=new_scheme,
                               netloc=new_netloc,
                               path=new_path)
            
            link = urlunsplit(url)

            if not self.is_iternal(link):
                continue

            if link.endswith('/'):
                link = link[:-1]
                        
            if link not in conversion_links:
                conversion_links.append(link)

        return conversion_links

    def check(self, link: str) -> bool:
        return all([link not in self.visited,
                    link not in self.not_response,
                    link not in self.queue])

    def _read_link(self, link: str) -> None:
        self.queue.pop(0)
        print('Processing ' + link)

        try:
            response = urllib.request.urlopen(link, timeout=5)
        
        except timeout:
            return

        except HTTPError:
            self.not_response.append(link)
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
        
        self.queue.extend([link for link in links if self.check(link)])

    def get_all_links(self) -> None:
        while self.queue:
            threads = []
                            
            for i in range(1, self.threads+1):
                if not self.queue:
                    break

                thread = threading.Thread(target=self._read_link, 
                                          args=(self.queue[0],))
                thread.start()
                threads.append(thread)
                            
            [thread.join() for thread in threads]
        
    def save_to_txt(self) -> None:
        with open(f'{self.netloc}.txt', 'x') as file:
            file.write('\n'.join([link for link in sorted(self.visited)]))
        
    
if __name__ == '__main__':
    url = ''
    threads = 1

    start_time = time.time()
    
    crawler = Crawler(url, threads)
    crawler.get_all_links()

    print(time.time() - start_time)
    
    crawler.save_to_txt()