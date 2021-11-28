from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import scrapy
from ekitenScrapy.items import EkitenscrapyItem
from ..middlewares import *
from ..JisCode import JisCode
from ..selenium_middleware import SeleniumMiddlewares
class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/'] #一旦試験的に、徳島のみ。

#    def start_requests(self):
#        """Summary Lines
#        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
#        Yields:
#            str: middlewareで返却された小ジャンルURL
#        """
#        middleware = SeleniumMiddlewares(['徳島県'], 4)
#        result = middleware.run()
#        counetr = 0
#        for url in result:
#            yield scrapy.Request(url)
#            counetr += 1
#            if counetr == 3:
#                break
        
        
    def parse(self, response):
        #self.start_urls = self.search(response)
        item = EkitenscrapyItem()
        item['store_link'] = response.css('div.shop-list-item-inner')
        yield item