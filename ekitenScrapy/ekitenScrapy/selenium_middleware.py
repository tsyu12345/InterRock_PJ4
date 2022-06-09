from __future__ import annotations
from typing import Any, Final as const

from abc import ABCMeta, abstractmethod
from multiprocessing.managers import ValueProxy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from JisCode import JisCode

import time



#TODO: 自作middlewareの実行中に発生したエラーを捕捉してGUIに通知する。
#TODO:一定時間起動後、403エラーが発生した場合、自動的にwebdriverを再起動する。
class AbsExtraction(object, metaclass=ABCMeta):
    """Summary Line:\n
    クローラーの中間処理を実装する抽象クラス。
    遷移先のページリンクを取得するときに、JavaScriptで動的に生成される場合に利用する。\n
    継承先の各子クラスで、レベル別（市区町村、大ジャンル、小ジャンル）に実際の抽出処理を実装する。\n
    """
    
    RETRY_UPPER_LIMIT:int = 3
    RESTART_WAIT_TIME:int = 300 #秒
    
    def __init__(self):
        #driver_absolute_path:str = chromedriver_binary.chromedriver_filename 
        #self.driver_path:const[str] = resource_path("../../bin/chromedriver.exe")
        self.driver_path = "./bin/chromedriver.exe"
        print(self.driver_path)
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
        #browser_path = resource_path('../../bin/chrome-win/chrome.exe')
        browser_path = './bin/chrome-win/chrome.exe'
        self.options.binary_location = browser_path
        
    @abstractmethod
    def extraction(self) -> list:
        """Summary Line.\n
        リンクを取得するメソッド。\n
        Returns:\n
            list:リンクのリスト\n
        """
        pass
    
    @abstractmethod
    def restart_driver(self) -> None:
        """Summary Line.\n
        ブラウザを終了し、webDriverの再起動をする。\n
        """
        pass

class BrowserRetryError(Exception):
    """Summary Line.\n
    再試行が失敗したときに出す例外\n
    """
    pass
        
class CityUrlExtraction(AbsExtraction):
    
    def __init__(self):
        super().__init__()
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
    
        
    def __CityLinkExtraction(self, pref_code:int) -> list[str]:
        """Summary Line.\n
        指定都道府県で、市区町村レベルのリンクを取得する際の処理コード。\n
        Args:\n
            pref_code (int):取得する市区町村の都道府県コード\n
        Returns:\n
            list:市区町村レベルのリンクのリスト\n
        """
        url:str = 'https://www.ekiten.jp/area/a_prefecture' + str(pref_code) + '/'
        urls:list[str] = []
        
        def get_href() -> None:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20) #waitオブジェクトの生成, 最大20秒待機
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'l-side_contents_search_tooltip_inner')))
            link_tags = self.driver.find_elements_by_css_selector('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > div.grouped_list_body > ul > li > a')
            print(link_tags)
            for tag in link_tags:
                urls.append(tag.get_attribute('href'))
        
        #FIXME:selenium timeout Exception が発生する↓。 <-403 サーバーブロックが原因
        for retry_counter in range(self.RETRY_UPPER_LIMIT):
            try:
                get_href()
            except TimeoutException:
                print("city link extraction timeout.")
                print("after 5 min, this process will be retried automatically.")
                self.restart_driver()
                time.sleep(self.RESTART_WAIT_TIME)
            else:
                break
        else:
            raise BrowserRetryError("市区町村レベルのリンク抽出に失敗しました。")
            
        self.driver.quit()
        return urls
        
    def extraction(self, pref_name:str) -> list[str]:
        """Summary Line.\n
        指定都道府県のリンクを取得し、そのリストを返却する。\n
        メソッド__CityLinkExtraction()の呼び出し処理。\n
        
        Args:\n
            pref_name (str):取得する市区町村の都道府県名\n
        Returns:\n
            list:市区町村レベルのリンクのリスト[url, url,....]\n
        """
        jis = JisCode()
        jis_code:int = jis.get_jis_code(pref_name)
        url_list = self.__CityLinkExtraction(jis_code)
        return url_list
    
    def restart_driver(self) -> None:
        
        self.driver.quit()
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
    


class AreaUrlExtraction(AbsExtraction):#TODO:[都道府県/市区町村]の文字列を抽出するコードの記載。
    """_summary_\n
    [都道府県/市区町村]の文字列を抽出する
    """
    
    def __init__(self, city_list:list[str]):
        super().__init__()
        self.city_list = city_list
        
        self.driver: const = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
        self.wait: const = WebDriverWait(self.driver, 20)
        
    
    def extraction(self) -> list[str]:
        
        results: list[str] = []
        
        for city_url in self.city_list:
            self.driver.get(city_url)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.l-side_contents_search_tooltip_inner')))
            
            #１つジャンルリンクへ遷移すると、目的の文字列が手に入るので、それを抽出する。
            genre_a_tag = self.driver.find_element_by_css_selector('div.l-side_contents_search_tooltip_inner > div > ul.l-side_contents_search_images > li > a')
            url: str = genre_a_tag.get_attribute('href')
            pref: const[str] = url.split("/")[4]
            city: const[str] = url.split("/")[5]
            results.append(pref + "/" + city + "/")
        
        self.driver.quit()
        print(results)
        return results
        
    def restart_driver(self):
        pass

class SeleniumMiddlewares(): #TODO:small_junle_extractionの廃止。と[都道府県/市区町村]の文字列を返却する使用に変更。
    
    def __init__(self, area_list:list[str], progress_num_value:ValueProxy[int]) -> None:
        """[summary]\n
        各実装クラスのインスタンスを生成し、それぞれのインスタンスに対して抽出処理を実行する。\n
        Args:\n
            area_list ([str]): 都道府県のリスト\n
        """
        self.area_list = area_list
        
        self.progress_num = progress_num_value
        
        self.results: list[str] = []
        
        
    def run(self) -> list[str]:
        """_summary_\n
        [都道府県/市区町村]の文字列を抽出する
        Returns:
            list[str]
        """
        city_extraction = CityUrlExtraction()
        
        for area in self.area_list:
            
            city_urls: list[str] = city_extraction.extraction(area)
            
            area_url_extraction = AreaUrlExtraction(city_urls)
            self.results.extend(area_url_extraction.extraction())
        
        return self.results
    
    
if __name__ == '__main__':
    """
    list1 = [
        ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県'], 
        ['福島県', '茨城県', '栃木県', '群馬県', '埼玉県'], 
        ['千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県',], 
        ['山梨県', '長野県', '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府'], 
        ['兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県'], 
        ['山口県', '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']
        ]
    newlist = list_split(3, list1)
    print(newlist)
    """
    #Test call
    t = AreaUrlExtraction(["https://www.ekiten.jp/area/a_city36204/"])
    t.extraction()