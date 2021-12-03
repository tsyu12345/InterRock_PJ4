from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import scrapy
import time
from ekitenScrapy.items import EkitenscrapyItem
from ..middlewares import *
from ..JisCode import JisCode
from ..selenium_middleware import SeleniumMiddlewares

class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/']
    MAX_RRTRYCOUNT = 3
    RETEYED = 0
    """
    def start_requests(self):
        Summary Lines
        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
        Yields:
            str: middlewareで返却された小ジャンルURL
        
        middleware = SeleniumMiddlewares(['徳島県'], 4)
        result = middleware.run()
        for url in result:
            yield scrapy.Request(url, callback=self.pre_parse, errback=self.error_parse)
    """ 
    def error_parse(self, failure):
        """Summary Lines
        scrapy.Requestで例外発生時（response.stasusが400、500台）にcallbackする。\n
        一定時間後にリトライリクエストする。\n
        Args:
            failure (scrapy.Request): scrapy.Request
        """
        print("####400 error catch####")
        print("request waiting for 20s")
        while self.RETEYED < self.MAX_RRTRYCOUNT:
            time.sleep(20)
            response = failure.value.response
            yield scrapy.Request(
                response.url, 
                callback=self.pre_parse, 
                errback=self.error_parse, 
                dont_filter=True)
            self.RETEYED += 1 
          
    def parse(self, response):
        """Summary Lines
        店舗検索処理。スクレイピング処理をする店舗URLを取得する。
        Args:
            response (scrapy.Request): scrapy.Requestでyieldされたresonseオブジェクト

        Yields:
            scrapy.Request: スクレイピング先URL
        """
        #self.start_urls = self.search(response)
        print(type(response.status))
        self.RETEYED = 0 #成功したらリトライカウントをリセット
        item = EkitenscrapyItem()
        parse_urls = []
        for elm in response.css('div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            href = elm.css('a::attr(href)').extract_first()
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse, errback=self.error_parse)
        
        #次のページがあるかどうか
        next_page = response.css('div.p-pagination_next > a.button')
        print(type(next_page))
        if next_page is not []:
            print("#####next page#####")
            next_page_url = response.urljoin(next_page[0].css('a::attr(href)').extract_first())
            print(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse, errback=self.error_parse)
        
            
            
    """
    def parse(self, response):
       Summary Lines
        本スクレイピング処理。店舗のページにアクセスして情報をitemsに格納する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
       
        item = EkitenscrapyItem()
        print("#####parse#####")
    """