import scrapy


class SecondspyderSpider(scrapy.Spider):
    name = 'SecondSpyder'
    allowed_domains = ['blog.scrapinghub.com']
    start_urls = ['http://blog.scrapinghub.com/']

    def parse(self, response):
        for older_link in response.css('.post-listing .post-item'):
            print(older_link)
            yield Post(
                url=post.css('div.post-header a::attr(href)').extract_first().strip(),
            )
        older_link = response.css('.blog-pagination a.next-posts-link::attr(href)').extract_first()
        if older_link is None:
            return 
        older_link = response.urljoin(older_link)
        yield scrapy.Request(older_link, callback=self.parse)
