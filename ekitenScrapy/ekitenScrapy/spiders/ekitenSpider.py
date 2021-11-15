import selenium
import scrapy
from ekitenScrapy.items import EkitenscrapyItem, StoreUrlItem
from ..middlewares import *
from ..selenium_middleware import *
class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/'] #一旦試験的に、徳島のみ。
    
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "ekitenScraapy.selenium_middleware.ScrapyMiddleware",
        },
        "DOWNLOAD_DELAY": 0.5,
    }
    
    def parse(self, response):
        item = EkitenscrapyItem() #本スクレイピング用
        preItem = StoreUrlItem() #遷移先URL格納用

        for url in response.css('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div'):
            #市区町村の絞り込み
            manufacUrl = url.css('a::attr(href)').extract_first()
            print(manufacUrl)
            #preItem['municipalities'] = response.urljoin(manufacUrl)
            item['store_link'] = response.urljoin(manufacUrl)
            yield item

    def closed(self, reason):
        SelenDriver.driver_quit()