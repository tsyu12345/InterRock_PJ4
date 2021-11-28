from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 

#Sample Codes

process = CrawlerProcess(get_project_settings())

process.crawl('ekiten')
process.start() # the script will block here until the crawling is finished
