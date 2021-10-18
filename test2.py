from selenium import webdriver
from bs4 import BeautifulSoup, element
import time
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
def test1():
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
    browser_path = 'chrome-win/chrome.exe'
    options.binary_location = browser_path
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
    driver.get('https://www.ekiten.jp/shop_63474300/')
    wait = WebDriverWait(driver, 20)
   
    iframe = driver.find_element_by_tag_name('iframe')
    driver.switch_to.frame(iframe)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    elm = soup.select_one('#mapDiv')
    print(elm)
    
    driver.quit()

def calcLatLong(address:str):
    """
    using geocoding.jp API.
    this function return [latitude ,longitude].
    if callback error from API or return ConnectionError, will return ['取得失敗', '取得失敗'].       
    """
    url = 'http://www.geocoding.jp/api/'
    payload = {'q':address}
    try:
        html = requests.get(url, params=payload)
    except:
        time.sleep(60)
        try:
            html = requests.get(url, params=payload)
        except:
            return ['取得失敗', '取得失敗']
    soup = BeautifulSoup(html.content, 'lxml')
    if soup.find('error'):
        return ['取得失敗', '取得失敗']
    else:
        try:
            lat = soup.find('lat').string  #緯度
            long = soup.find('lng').string #経度
            return [lat, long]
        except AttributeError:
            return ['取得失敗', '取得失敗']

def test3():
    s = ""
    s2 = s.split(' ')
    print(s)
    print(s2)
test1()
#print(calcLatLong('徳島県阿南市羽ノ浦町中庄黒松７６−１'))    
#test3()