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
    start_urls = ['https://www.ekiten.jp/cat_golf/tokushima/ananshi/']
    MAX_RRTRYCOUNT = 3
    RETEYED = 0
    
    def start_requests(self):
        """Summary Lines
        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
        Yields:
            str: middlewareで返却された小ジャンルURL
        """
        middleware = SeleniumMiddlewares(['徳島県'], 4)
        result = middleware.run()
        for url in result:
            yield scrapy.Request(url, callback=self.pre_parse, errback=self.error_parse)
        
    def error_parse(self, failure):
        """Summary Lines
        scrapy.Requestで例外発生時（response.stasusが400、500台）にcallbackする。
        Args:
            failure (scrapy.Request): scrapy.Request
        """
        print("####400 error catch####")
        print("request waiting for 20s")
        while self.RETEYED < self.MAX_RRTRYCOUNT:
            time.sleep(20)
            response = failure.value.response
            yield scrapy.Request(response.url, callback=self.pre_parse, errback=self.error_parse)
            self.RETEYED += 1 
          
    def pre_parse(self, response):
        """Summary Lines
        店舗検索処理。スクレイピング処理をする店舗URLを取得する。
        Args:
            response (scrapy.Request): scrapy.Requestでyieldされたresonseオブジェクト

        Yields:
            scrapy.Request: スクレイピング先URL
        """
        #self.start_urls = self.search(response)
        print(type(response.status))
        self.RETEYED = 0
        item = EkitenscrapyItem()
        for elm in response.css('div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            href = elm.css('a::attr(href)').extract_first()
            url = response.urljoin(href)
            yield scrapy.Request(url)
    
    def parse(self, response):
        """Summary Lines
        本スクレイピング処理。店舗のページにアクセスして情報をitemsに格納する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
        """