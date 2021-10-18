import scrapy


class ScrapyBlogSpiderSpider(scrapy.Spider):
    name = 'scrapy_blog_spider'
    #allowed_domains = ['blog.scrapinghub.com']
    start_urls = ['http://qiita.com/advent-calendar/2015/categories/programming_languages']

    def parse(self, response):
        for href in response.css('.adventCalendarList .adventCalendarList_calendarTitle > a::attr(href)'):
            
