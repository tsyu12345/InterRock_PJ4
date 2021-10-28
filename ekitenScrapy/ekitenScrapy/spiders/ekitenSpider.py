import scrapy
from ekitenScrapy.items import EkitenscrapyItem

class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/']

    def parse(self, response):
        item = EkitenscrapyItem()
        for href in response.css('body > div.l-wrapper > div > div.l-contents_wrapper > main > div > div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            #print(href)
            store_urlId = href.css('a::attr(href)').extract_first()
            item['store_link'] = response.urljoin(store_urlId)
            yield item

