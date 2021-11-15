from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class SelenDriver():
    
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')
        
    def get_dom(self, query):
        dom = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, query)))
        return dom

    def driver_quit(self):
        self.driver.delete_all_cookies()
        self.driver.quit()
    
    def get_page(self, url):
        self.driver.get(url)
class ScrapyMiddleware(object):
    
    def process_request(self, request, spider):
        driver = SelenDriver()
        driver.driver.get(request.url)
        return HtmlResponse(driver.driver.current_url, body=driver.driver.page_source, encoding='utf-8', request=request)
    

