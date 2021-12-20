#Scrapy関係のインポート
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 

#GUI関係のインポート
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, popup, popup_error
import sys
from multiprocessing import Pool, freeze_support
import threading as th

class SpiderCall:
    """
    Summary:\n
    Spyderを実行する。およびその関連機能の呼び出し、参照を行う。
    """
    def __init__(self, pref_list:list):
        settings = get_project_settings()
        settings.set('FEED_URI', 'results_TEST.csv')
        self.process = CrawlerProcess(get_project_settings())
        self.process.crawl('ekitenSpider', prefectures=pref_list)
        
    def run(self):
        self.process.start() # the script will block here until the crawling is finished
    

if __name__ == '__main__':
    spider = SpiderCall(['徳島県'])