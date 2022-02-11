from importlib.resources import path
from pydoc import visiblename
from time import time
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 
from scrapy.statscollectors import StatsCollector
from RequestTotalCount import RequestTotalCount
import pathlib
from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from ekitenScrapy.spiders.ekitenSpider import EkitenspiderSpider

#スレッド関係のインポート
from multiprocessing import Pool, freeze_support, Manager

class SpiderCall: #TODO:中止処理の追加
    """
    旧スパイダー実行クラス。現在はRunnerでの構築中。
    Summary:\n
    Spyderを実行する。およびその関連機能の呼び出し、参照を行う。
    Args:\n
        pref_list(list[str]): 都道府県のリスト\n
        save_path(str): スクレイピング結果の保存先\n
        junle(str): スクレイピングするジャンル\n
    """
    def __init__(self, pref_list:list, save_path:str, junle:str):
        self.pref_list = pref_list
       
        maneger = Manager()
        self.counter = maneger.Value('i', 0) #現在の進捗状況のカウンター
        self.total_counter = maneger.Value('i', 1) #スクレイピングするサイトの総数
        self.loading_flg = maneger.Value('b', False) #ローディング中かどうかのフラグ
        self.end_flg = maneger.Value('b', False) #中断のフラグ
        settings = get_project_settings()
        settings.set('FEED_FORMAT', 'xlsx')
        settings.set('FEED_URI', save_path)
        #settings.set('FEED_EXPORT_ENCODING', 'utf-8')
        
        self.process = CrawlerProcess(settings=settings)
        self.process.crawl('ekitenSpider',)
        
    def run(self):
        #検索総数を取得6
        count = RequestTotalCount(self.pref_list).get_count()
        print("totalCount: "+str(count))
        self.total_counter.value = count
        
        self.process.start() # the script will block here until the crawling is finished

    def stop(self):
        self.end_flg.value = True

def main():
    test = SpiderCall(['徳島県'],'test.xlsx', '全てのジャンル')
    test.run()
    
    
    
if __name__ == "__main__":
    #main()
    testDic:dict = {
        "test":3
    }
    print(testDic["test"])