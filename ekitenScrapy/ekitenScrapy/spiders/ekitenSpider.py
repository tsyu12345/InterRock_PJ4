import scrapy
from ekitenScrapy.items import EkitenscrapyItem, StoreUrlItem
from ..selenium_middleware import quitDriver
class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/'] #一旦試験的に、徳島のみ。
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "some_crawler.selenium_middleware.SeleniumMiddleware": 0,
        },
        "DOWNLOAD_DELAY": 0.5,
    }
    def parse(self, response):
        item = EkitenscrapyItem() #本スクレイピング用
        preItem = StoreUrlItem() #遷移先URL格納用

        for url in response.css('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > div.grouped_list_body > ul > li > a'):
            #市区町村の絞り込み
            manufacUrl = url.css('a::attr(href)').extract_first()
            print(manufacUrl)
            #preItem['municipalities'] = response.urljoin(manufacUrl)
            item['store_link'] = response.urljoin(manufacUrl)
            yield item

    def closed(self, reason):
        quitDriver()