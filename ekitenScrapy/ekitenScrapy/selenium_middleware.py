from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def js_execute(url):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument('--disable-extensions')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    browser_path = 'C:/Users/syuku/ProdFolder/InterRock_PJ4/chrome-win/chrome.exe'
    options.binary_location = browser_path
    driver = webdriver.Chrome(executable_path='C:/Users/syuku/ProdFolder/InterRock_PJ4/chromedriver.exe', options=options)
    driver.get(url)
    print(driver.find_elements_by_css_selector('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > div.grouped_list_body > ul > li > a'))
    
class ScrapyMiddleware(object):
    
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("start-maximized")
        self.options.add_argument("enable-automation")
        #self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument('--disable-extensions')
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-browser-side-navigation")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        prefs = {"profile.default_content_setting_values.notifications": 2}
        self.options.add_experimental_option("prefs", prefs)
        browser_path = 'C:/Users/syuku/ProdFolder/InterRock_PJ4/chrome-win/chrome.exe'
        self.options.binary_location = browser_path
        self.driver = webdriver.Chrome(executable_path='C:/Users/syuku/ProdFolder/InterRock_PJ4/chromedriver.exe', options=self.options)
    
    def process_request(self, request, spider):
        self.driver.get(request.url)
        print("Hello")
        return HtmlResponse(self.driver.current_url, body=self.driver.page_source, encoding='utf-8', request=request)
        
    

