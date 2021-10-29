import scrapy
from ekitenScrapy.items import EkitenscrapyItem, StoreUrlItem

class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/'] #一旦試験的に、徳島のみ。

    def parse(self, response):
        item = EkitenscrapyItem() #本スクレイピング用
        preItem = StoreUrlItem() #遷移先URL格納用

        for url in response.css('body > div.l-wrapper > div > div.l-contents_wrapper > main > div.box p-shop_box > div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            #市区町村の絞り込み
            manufacUrl = url.css('a::attr(href)').extract_first()
            print(manufacUrl)
            #preItem['municipalities'] = response.urljoin(manufacUrl)
            item['store_link'] = response.urljoin(manufacUrl)
            yield item

