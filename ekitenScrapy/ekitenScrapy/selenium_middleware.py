from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup as Soup
from JisCode import JisCode
import requests
import os
import sys

def resource_path(relative_path):
    """
    バイナリフィルのパスを提供
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def list_split(n:int, l:list) -> tuple:
    """Summary Line:\n
    リストを指定数に分割し、そのタプルを返却する。
    Args:\n
        n (int): 分割数\n
        l (list): 分割対象のリスト\n
    Returns:\n
        tuple: 分割されたリストを格納したタプル\n
    """
    return tuple([l[i:i + n] for i in range(0, len(l), n)])
    
class SeleniumMiddleware(object):
    """Summary Line:\n
    遷移先のページリンクを取得するときに、JavaScriptで動的に生成される場合に利用する。\n
    各メソッドを実行し、それぞれのリンクを取得する。\n
    ＜呼び出し可能メソッド一覧＞※各メソッドの引数は、それぞれのメソッドの説明を参照。\n
    ・city_list(pref_name) -> 市区町村URLのリスト\n
    ・big_junle_list(city_url_list) -> 市区町村ごとの大ジャンルURLを格納した２次元リスト\n
    ・準備中\n
    
    """
    
    def __init__(self):
        self.driver_path = 'C:/Users/syuku/ProdFolder/InterRock_PJ4/chromedriver.exe'
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("start-maximized")
        self.options.add_argument("enable-automation")
        self.options.add_argument("--headless")
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
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
    
    def __callJisCode(self, pref_name) -> int:
        """Sumary Line.\n
        指定都道府県の名前から、都道府県コードを取得する。\n
        Args:\n
            pref_name (str):取得する都道府県の名前\n
        Returns:\n
            int:都道府県コード\n
        """
        
        jis_code = JisCode(pref_name)
        return jis_code
        
    def __CityLinkExtraction(self, pref_code:int) -> list:
        """Summary Line.\n
        指定都道府県で、市区町村レベルのリンクを取得する際の処理コード。\n
        Args:\n
            pref_code (int):取得する市区町村の都道府県コード\n
        Returns:\n
            list:市区町村レベルのリンクのリスト\n
        """
        
        url = 'https://www.ekiten.jp/area/a_prefecture' + str(pref_code) + '/'
        wait = WebDriverWait(self.driver, 20) #waitオブジェクトの生成, 最大20秒待機
        self.driver.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'l-side_contents_search_tooltip_inner')))
        link_tags = self.driver.find_elements_by_css_selector('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > div.grouped_list_body > ul > li > a')
        print(link_tags)
        urls = []
        for tag in link_tags:
            urls.append(tag.get_attribute('href'))
        return urls
        
    def city_list(self, pref_name:str) -> list:
        """Summary Line.\n
        指定都道府県のリンクを取得し、そのリストを返却する。\n
        メソッド__CityLinkExtraction()の呼び出し処理。\n
        
        Args:\n
            pref_name (str):取得する市区町村の都道府県名\n
        Returns:\n
            list:市区町村レベルのリンクのリスト\n
        """
        jis_code = self.__callJisCode(pref_name)
        url_list = self.__CityLinkExtraction(jis_code)
        return url_list
    
    def big_junle_list(self, city_url_list:list) -> list:
        """[summary]\n

        Args:\n
            city_url ([str]): 取得したい市区町村のURLのリスト\n

        Returns:\n
            list: 市区町村ごとの取得した大ジャンルごとのURL２次元リスト[[url, url...], [some,....]]\n
        """
        result_list = self.__big_junle_link_extraction(city_url_list)
        return result_list
            

    def __big_junle_link_extraction(self, city_list:list) -> list:
        """[summary]\n
        市区町村の大ジャンルリンクを抽出し、そのリンクのリストを返す処理。\n
        Args:\n
            url (list): 市区町村のURLリスト\n
        Returns:\n
            list: 市区町村ごとの大ジャンルリンクのリスト\n
        """
        url_list = []
        for url in city_list:
            print(url)
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20) #waitオブジェクトの生成, 最大20秒待機
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'l-side_contents_search_tooltip_inner')))
            a_tags = self.driver.find_elements_by_css_selector('div.l-side_contents_search_tooltip_inner > div > ul.l-side_contents_search_images > li > a')
            add_links = [] 
            for a in a_tags:
                add_links.append(a.get_attribute('href'))
            url_list.append(add_links)
        return url_list

    
    def small_junle_list(self, big_junle_list:list) -> list:
        """[summary]\n
        大ジャンルごとのリンクを参照し、その遷移先の小ジャンルのリンクを返却する。
        Args:\n
            big_junle_list(list):大ジャンルのURLリスト\n
        Returns:\n
            list: 小ジャンルごとのURLリスト\n
        """
        url_list = []
        for big_junle_url_list in big_junle_list:
            for url in big_junle_url_list:
                url_list.append(self.__small_junle_link_extraction(url))
        return url_list
        
    
    def __small_junle_link_extraction(self, url:str) -> list:
        """[summary]\n
        大ジャンルリンク先の小ジャンルリンクを抽出し、そのリンクのリストを返す処理。\n
        Args:\n
            url (str): 大ジャンルのURL\n
        Returns:\n
            list: 大ジャンルごとの中小ジャンルリンクリスト\n
        """
        result_list = []
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 20) #waitオブジェクトの生成, 最大20秒待機
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(2) > ul > li:nth-child(2) > div > div > div > div > div > ul')))
        a_tags = self.driver.find_elements_by_css_selector('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(2) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > a') 
        for a in a_tags:
            result_list.append(a.get_attribute('href'))
        #for url in big_junle_url_list:
        return result_list
 
    def quitDriver(self) -> None:
        """Summary Line.\n
        ブラウザを終了する。\n
        """
        self.driver.quit()

if __name__ == '__main__':
    list1 = ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']
    newlist = list_split(3, list1)
    print(newlist)
"""
    #Test call
    selenium_middle = SeleniumMiddleware()
    result_city = selenium_middle.city_list('徳島県')
    print(result_city)
    result_big_junle = selenium_middle.big_junle_list(result_city)
    print(result_big_junle)
    result_small_junle = selenium_middle.small_junle_list(result_big_junle)
    print(result_small_junle)
    selenium_middle.quitDriver()
""" 