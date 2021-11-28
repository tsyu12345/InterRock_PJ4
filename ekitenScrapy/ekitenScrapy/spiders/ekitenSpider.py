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
    #start_urls = [] #一旦試験的に、徳島のみ。
    
    """
    custom_settings = {
        "DOWNLOAD_MIDDLEWARE": {
            "ekitenScrapy.selenium_middleware.ScrapyMiddleware"
        },
    }
    """
    def start_requests(self):
        """Summary Lines
        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
        Yields:
            str: middlewareで返却された小ジャンルURL
        """
        middleware = SeleniumMiddlewares(['徳島県'], 4)
        result = middleware.run()
        for url in result:
            yield scrapy.Request(url)
        
        
    def parse(self, response):
        #self.start_urls = self.search(response)
            
        item = EkitenscrapyItem()
        for url in response.css('body > div.l-wrapper > div > div.l-contents_wrapper > main > div.p-shop_content_container.p-shop_content_container_relative > table > tbody > tr:nth-child(3) > td'):
            #市区町村の絞り込み
            manufacUrl = url.css('td::text').extract_first()
            #preItem['municipalities'] = response.urljoin(manufacUrl)
            item['store_link'] = manufacUrl
            #item['store_link'] = response.urljoin(manufacUrl)
            yield item
        
            
   