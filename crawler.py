from bs4 import BeautifulSoup
import requests
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
# import logging
import argparse
import pathlib

class Crawler:

    def __init__(self, starting_url='https://www.rescale.com/', max_workers=None, test=False):
        self.starting_url = starting_url
        self.seen = set()
        self.max_workers = max_workers
        self.queue = deque()
        self.queue.append(starting_url)
        self.requests = requests
        self.prefix = 'http'
        self.test = test
        if self.test:
            self.requests = TestRequester()
            self.prefix = 'test'
            self.output = dict()

    def crawl(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while len(self.queue) > 0:
                visits = set()
                while len(self.queue) > 0:
                    url = self.queue.popleft()
                    visits.add(executor.submit(self.visit, url))
                for visit in concurrent.futures.as_completed(visits):
                    parent, children = visit.result()
                    if parent is None:
                        continue
                    print(parent)
                    for child in children:
                        print('\t%s' % child)
                        if child not in self.seen:
                            self.queue.append(child)
                            self.seen.add(child)
                    if self.test:
                        self.output[parent] = frozenset(children)
        if self.test:
            return self.output


    def visit(self, url):
        try:
            r = self.requests.get(url)
        except requests.exceptions.SSLError:
            return None, None
        bs = BeautifulSoup(r.text, features="html.parser")
        urls = set()
        for link in bs.find_all('a'):
            _url = link.get('href')
            if _url is not None and _url[:4] == self.prefix:
                urls.add(_url)
        return url, urls

class TestRequester:

    def __init__(self):
        self.fake_webpath = str(pathlib.Path(__file__).parent.absolute()) + '/fake_website/'
        print(self.fake_webpath)

    def get(self, file):
        with open(self.fake_webpath + file) as f:
            return TestResponse(f.read())


class TestResponse:

    def __init__(self, text):
        self.text = text

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Crawls website and logs urls.')
    parser.add_argument('--starting-url', default='https://www.rescale.com/', help='url to start crawling on.')
    parser.add_argument('--test', default=False, action='store_true', help='run in test mode.')
    parser.add_argument('--max-workers', default=4, type=int, help='max number of workers.')
    args = parser.parse_args()
    print(args)
    crawler = Crawler(starting_url=args.starting_url, max_workers=args.max_workers, test=args.test)
    crawler.crawl()

    # test_requester = TestRequester()
    # print(test_requester.get('atest.html'))