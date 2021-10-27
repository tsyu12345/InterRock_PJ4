from HTBscrapy.items import HtbscrapyItem
import scrapy


class HtbspiderSpider(scrapy.Spider):
    name = 'HTBSpider'
    allowed_domains = ['beauty.hotpepper.jp']
    start_urls = ['https://beauty.hotpepper.jp/CSP/bt/freewordSearch/?freeword=%E6%9D%B1%E4%BA%AC%E9%83%BD&searchGender=ALL&pn=1']

    def parse(self, response):
        item = HtbscrapyItem()
        item['page_url'] = response.css('#mainContents > ul > li > div.slnCassetteHeader > h3 > a::text')
        yield item