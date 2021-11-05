import os.path

from urlparse import urlparse

import arrow

from selenium import webdriver
from scrapy.http import HtmlRsesponse

driver = webdriver.Chrome()

class SeleniumMiddleware(object):

    def process_request(self, request, spider):
        driver.get(request.url)
        return HtmlRsesponse(driver.current_url, body=driver.page_source, encoding='utf-8', request=request)
    
    def quitDriver():
        driver.quit()