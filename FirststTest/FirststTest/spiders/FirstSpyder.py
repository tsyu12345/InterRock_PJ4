import scrapy


class FirstspyderSpider(scrapy.Spider):
    name = 'FirstSpyder'
    allowed_domains = ['https://imagisi.com/']
    start_urls = ['http://https://imagisi.com//']

    def parse(self, response):
        for href in response.css('.a-wrap'):
            yield {
                'url':href.css('a::attr(href)').extract_first(),
                'title':href.css('h2.entry-card-title::text').extract_first()
            }
        older_link = response.css('div.pagination-next a.pagination-next-link::attr(href)').extract_first()
        if older_link is None:
            return 
        older_link = response.urljoin(older_link)
        yield scrapy.Request(older_link, callback=self.parse)
