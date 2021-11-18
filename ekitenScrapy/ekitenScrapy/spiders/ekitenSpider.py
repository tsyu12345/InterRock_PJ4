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
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/'] #一旦試験的に、徳島のみ。
    
    """
    custom_settings = {
        "DOWNLOAD_MIDDLEWARE": {
            "ekitenScrapy.selenium_middleware.ScrapyMiddleware"
        },
    }
    """

        
    def parse(self, response):
        print("OHHHHHHHHHHHHHHHHHH")
        item = EkitenscrapyItem()
        for url in response.css('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > div.grouped_list_body > ul > li > a'):
            #市区町村の絞り込み
            manufacUrl = url.css('a::attr(href)').extract_first()
            #preItem['municipalities'] = response.urljoin(manufacUrl)
            item['store_link'] = manufacUrl
            yield item
            
            
    def closed(self, reason):
        ScrapyMiddleware().driver.quit()