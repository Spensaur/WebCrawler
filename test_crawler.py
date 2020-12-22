from crawler import Crawler
import unittest
import pathlib
import subprocess

class TestCrawler(unittest.TestCase):

    def test_crawler(self):
        correct_output = {
            'testa.html': frozenset({'testb.html'}),
            'testb.html': frozenset({'testc.html', 'testd.html'}),
            'testc.html': frozenset({'testb.html', 'testa.html'}),
            'testd.html': frozenset({'testb.html', 'testa.html'})}
        crawler = Crawler(starting_url='testa.html', test=True)
        output = crawler.crawl()
        assert output == correct_output

if __name__ == '__main__':
    unittest.main()