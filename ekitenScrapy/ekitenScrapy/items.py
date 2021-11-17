# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EkitenscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
    結果出力用Item、本スクレイピング用
    """
    store_link = scrapy.Field() #scrapingする掲載URL



