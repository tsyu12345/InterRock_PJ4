import scrapy


class SecondspyderSpider(scrapy.Spider):
    name = 'SecondSpyder'
    allowed_domains = ['blog.scrapinghub.com']
    start_urls = ['http://blog.scrapinghub.com/']

    def parse(self, response):
        pass
