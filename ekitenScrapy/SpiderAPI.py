#型注釈の有効化
from __future__ import annotations
from tokenize import Comment
from typing import Any, Optional, Iterator, Final as const

#Scrapy関係のインポート
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 
from scrapy.settings import Settings
from RequestTotalCount import RequestTotalCount
from Local import list_split
from ekitenScrapy.selenium_middleware import SeleniumMiddlewares
from ekitenScrapy.spiders.ekitenSpider import EkitenspiderSpider

#共有メモリのインポート
from multiprocessing.managers import SyncManager, ValueProxy

#スレッド関係のインポート
from multiprocessing import Manager

#ワークシート関係
from WorkBook import WorkBook, COLUMN_MENUS

#other
import time

class SpiderCall(): #TODO:中止処理の追加, CrawlerProcessの並列実行
    """
    旧スパイダー実行クラス。現在はRunnerでの構築中。
    Summary:\n
    Spyderを実行する。およびその関連機能の呼び出し、参照を行う。
    Args:\n
        pref_list(list[str]): 都道府県のリスト\n
        save_path(str): スクレイピング結果の保存先\n
        junle(str): スクレイピングするジャンル\n
    """
    
    FEED_EXPORT_FIELDS: const[list[str]] = [item_key for item_key in COLUMN_MENUS.keys()]
    FILE_FORMAT: const[str] = 'xlsx'
    FILE_EXTENSION: const[str] = '.' + FILE_FORMAT
    TEMP_DIR: const[str] = "./temp"
    
    def __init__(self, pref_list:list[str], save_path:str, junle:str):
        """_summary_\n
        Args:\n
            pref_list(list[str]): 都道府県のリスト\n
            save_path(str): スクレイピング結果の保存先\n
            junle(str): スクレイピングするジャンル -> まだ未実装。\n
        """
        self.pref_list = pref_list
        self.save_path = save_path #最終的な保存先
        self.junle = junle
        
        #Spider settings
        self.settings: Settings = get_project_settings()
        self.settings.set('FEED_FORMAT', self.FILE_FORMAT)
        self.settings.set('FEED_URI', '%(filename)s'  + self.FILE_EXTENSION)
        self.settings.set('FEED_EXPORT_FIELDS', self.FEED_EXPORT_FIELDS)
        self.settings.set('TELNETCONSOLE_ENABLED', False)
        
        #共有メモリ上の各フラグ、カウンタ変数の定義
        maneger:SyncManager = Manager()
        self.counter:ValueProxy[int] = maneger.Value('i', 0) #現在のクロール済みカウンター
        self.total_counter:ValueProxy[int] = maneger.Value('i', 1) #スクレイピングするサイトの総数
        self.loading_flg:ValueProxy[bool] = maneger.Value('b', False) #ローディング中かどうかのフラグ
        self.end_flg:ValueProxy[bool] = maneger.Value('b', False) #中断のフラグ
        self.progress_num:ValueProxy[int] = maneger.Value('i', 0) #進捗状況の表示用    
        
        #middlewareインスタンスの生成
        self.middleware = SeleniumMiddlewares(self.pref_list, self.progress_num)
        self.crawler = CrawlerProcess(self.settings)
        
        #分散クロール結果の一時保存先を格納したリスト
        self.crawler_temp_save_list:list[str] = []
    
    def __start_crawler(self, crawler_url_list:list[str], crawler_process_count:int) -> None:
        """_summary_\n
        分散クロール用に追加されるクローラーごとに異なる設定のクローラー設定を用意し、Scrapyに予約する。
        Args:\n
            crawler_url_list(list[str]): クロールするURLのリスト\n
            crawler_process_count(int): クローラーのプロセス数\n
        """
        crawl_list: list[list[str]] = list_split(crawler_process_count, crawler_url_list)        
        
        for crawler_id, url_list in enumerate(crawl_list):
            filename: str = self.TEMP_DIR + "/" + 'crawler_temp_save_' + str(crawler_id+1)
            print("CRAWL AREA LIST:", url_list)
            self.crawler.crawl(
                EkitenspiderSpider,
                self.counter, 
                self.loading_flg, 
                self.end_flg, 
                url_list, #type: list[str]
                comment='test',
                filename=filename,
            )
            filename = filename + self.FILE_EXTENSION #拡張子をつけてからリストへ格納。
            
            self.crawler_temp_save_list.append(filename)
        
        self.crawler.start()
        
        
    def run(self) -> None:
        """[summary]\n
        GUIの実行ボタンクリック後に実行される。
        Spider一連のスクレイピング処理を実行する。
        このメソッドは非同期で実行されたい。
        """
        #検索総数を取得
        self.loading_flg.value = True
        self.progress_num.value += 1
        count = RequestTotalCount(self.pref_list).get_count()
        print("totalCount: "+str(count))
        self.total_counter.value = count
        result = self.middleware.run()
        self.progress_num.value += 1
        
        #試験用
        """
        result = [
            "tottori/iwamigun/"
        ]
        """
        
        self.__start_crawler(result, 4)
        print("crawler exit")
        
        self.progress_num.value += 1
        self.__save_crawl_result()
        
    def stop(self):
        self.end_flg.value = True
        
        
    def __save_crawl_result(self):
        """_summary_\n 
        クロール結果を保存する。
        """
        workbook = WorkBook(self.save_path, self.crawler_temp_save_list)
        workbook.create_crawl_workbook()
        workbook.col_menulocalize()
        workbook.save()
        workbook.remove_temp_file()
        
        
if __name__ == "__main__":
    """
    _summary_\n
    TEST CALL
    GUIなしで実行する場合に使用する。
    """
    print("SPIDER START")
    test = SpiderCall(["徳島県"], "./TEST.xlsx", "NONE")
    test.run()
    print("SPIDER END")