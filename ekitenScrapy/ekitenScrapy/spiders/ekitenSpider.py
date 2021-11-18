from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import scrapy
from ekitenScrapy.items import EkitenscrapyItem
from ..middlewares import *
from ..selenium_middleware import *
class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/shop_6764092/'] #一旦試験的に、徳島のみ。
    
    """
    custom_settings = {
        "DOWNLOAD_MIDDLEWARE": {
            "ekitenScrapy.selenium_middleware.ScrapyMiddleware"
        },
    }
    """
        
        
    def parse(self, response):
       
        item = EkitenscrapyItem()
        for url in response.css('body > div.l-wrapper > div > div.l-contents_wrapper > main > div.p-shop_content_container.p-shop_content_container_relative > table > tbody > tr:nth-child(3) > td'):
            #市区町村の絞り込み
            manufacUrl = url.css('td::text').extract_first()
            #preItem['municipalities'] = response.urljoin(manufacUrl)
            item['store_link'] = manufacUrl
            #item['store_link'] = response.urljoin(manufacUrl)
            yield item
        
            
   