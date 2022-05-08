from __future__ import annotations
from typing import Any, Final as const

from abc import ABCMeta, abstractmethod
from multiprocessing.managers import ValueProxy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
#import chromedriver_binary 
from multiprocessing import Pool, freeze_support, TimeoutError
from multiprocessing.pool import ApplyResult

import time
import sys 
sys.path.append('../')
from Local import *
from .JisCode import JisCode
    


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
        
    def extraction(self, pref_name:str) -> list:
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
    
class BigJunleExtraction(AbsExtraction):
    
    
    
    def __init__(self):
        super().__init__()
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)

    def extraction(self, city_url_list:list) -> list:
        """[summary]\n

        Args:\n
            city_url ([str]): 取得したい市区町村のURLのリスト\n

        Returns:\n
            list: 市区町村ごとの取得した大ジャンルごとのURL２次元リスト[[url, url...], [some,....]]\n
        """
        result_list = self.__big_junle_link_extraction(city_url_list)
        return result_list
            

    def __big_junle_link_extraction(self, city_list:list[str]) -> list:
        """[summary]\n
        市区町村の大ジャンルリンクを抽出し、そのリンクのリストを返す処理。\n
        Args:\n
            url (list): 市区町村のURLリスト\n
        Returns:\n
            list: 市区町村ごとの大ジャンルリンクのリスト\n
        """
        url_list = []
        def get_href(url:str) -> None:
            print(url)
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20) #waitオブジェクトの生成, 最大20秒待機
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'l-side_contents_search_tooltip_inner')))
            a_tags = self.driver.find_elements_by_css_selector('div.l-side_contents_search_tooltip_inner > div > ul.l-side_contents_search_images > li > a')
            add_links = [] 
            for a in a_tags:
                add_links.append(a.get_attribute('href'))
            url_list.append(add_links)
                
        #FIXME:selenium timeout Exception が発生する↓。
        for url in city_list:
            
            for retry_counter in range(self.RETRY_UPPER_LIMIT):
                try:
                    get_href(url)
                except TimeoutException:
                    print("タイムアウト")
                    time.sleep(300)
                    self.restart_driver()
                else:
                    break
            else:
                raise BrowserRetryError("大ジャンルリンク抽出に失敗しました。")
                
        self.driver.quit()
        return url_list
    
    def restart_driver(self) -> None:
        
        self.driver.quit()
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
        
class SmallJunleExtraction(AbsExtraction):
    #TODO:multiprocessの関係上、このクラスのみdriverがローカル変数になっているので、親クラスの変更の繁栄が少し煩雑になっている。
    #TODO:現時点だと、URLの抽出処理全部が完了しないと次のリクエストを出せないようになっているため、時間がかかる。ここで抽出したＵＲＬをscrapy.Requestで投げるようにしたら終了を待たずにクロールできるかも。
    #TODO:GUI側で中止処理したときにdriver,browserを終了させるようにする。
    def _init__(self):
        super().__init__()
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)

    def extraction(self, big_junle_list:list) -> list:
        """[summary]\n
        大ジャンルごとのリンクを参照し、その遷移先の小ジャンルのリンクを返却する。\n
        Args:\n
            big_junle_list(list):大ジャンルのURLリスト\n
        Returns:\n
            list: 小ジャンルごとのURLリスト\n
        """
        result = self.__small_junle_link_extraction(big_junle_list)
        return result

        
    def __small_junle_link_extraction(self, url_list:list) -> list:
        """[summary]\n
        大ジャンルリンク先の小ジャンルリンクを抽出し、そのリンクのリストを返す処理。\n
        Args:\n
            url_list (list): 大ジャンルのURLリスト\n
        Returns:\n
            list: 大ジャンルごとの中小ジャンルリンクリスト\n
        """
        result_list = []
        driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
        
        def get_href() -> None:
            wait = WebDriverWait(driver, 20) #waitオブジェクトの生成, 最大20秒待機
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(2) > ul > li:nth-child(2) > div > div > div > div > div > ul')))
            a_tags = driver.find_elements_by_css_selector('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(2) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > a') 
            for a in a_tags:
                result_list.append(a.get_attribute('href'))
        
        def restart_driver(exist_driver:webdriver.Chrome) -> webdriver.Chrome:
            exist_driver.delete_all_cookies()
            exist_driver.quit()
            time.sleep(self.RESTART_WAIT_TIME)
            new_driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
            return new_driver
        
        for url in url_list:
            #FIXME:selenium timeout Exception が発生する↓。
            for retry_counter in range(self.RETRY_UPPER_LIMIT):
                try:
                    driver.get(url)
                    get_href()
                except TimeoutException:
                    print("small junle extraction timeout.")
                    print("after 5 min, this process will be retried automatically.")
                    driver = restart_driver(driver)                
                else: #try-exceptのelse部分
                    break
            else: #for文のelse部分
                raise BrowserRetryError("小ジャンルリンクの抽出に失敗しました。")
                
        driver.quit()
        return result_list

    def restart_driver(self) -> None:
        pass
        
class SeleniumMiddlewares():
    
    def __init__(self, area_list:list, process_count:int, progress_num_value:ValueProxy[int]) -> None:
        """[summary]\n
        各実装クラスのインスタンスを生成し、それぞれのインスタンスに対して抽出処理を実行する。\n
        Args:\n
            area_list ([str]): 都道府県のリスト\n
            process_count (int): 並列処理を行うブラウザの個数（推奨:１～４まで）\n
        """
        self.area_list = area_list
        self.process_count = process_count
        self.progress_num = progress_num_value
        self.p = Pool(self.process_count)
    
    
    def __procedure(self, area):
        """[summary]\n
        apply_asyncを使用して、小ジャンルクラスのインスタンスに対して抽出処理を実行する。\n
        Args:\n
            area (str): 対象都道府県\n

        Returns:\n
            list: その都道府県の小ジャンルごとのURLリスト\n
        """
        city_ext = CityUrlExtraction()
        big_junle_ext = BigJunleExtraction()
        small_junle_ext = SmallJunleExtraction()
        
        self.progress_num.value += 1
        city_list = city_ext.extraction(area)
        self.progress_num.value += 1
        big_junle_list = big_junle_ext.extraction(city_list)
        self.progress_num.value += 1
        big_junle_split_lists = list_split(self.process_count, big_junle_list)
        apply_results:list[ApplyResult] = []
        for splitElm in big_junle_split_lists:
            oned_list = convert2d_to_1d(splitElm)
            async_result:ApplyResult = self.p.apply_async(small_junle_ext.extraction, args=([oned_list]))
            apply_results.append(async_result)
        result = self.__join_process(apply_results)
        print(result)
        return result
    
    def stop(self):
        """[summary]\n 
        動作を停止させる。
        """
        
        self.p.terminate()
    
    def __join_process(self, apply_results:list[ApplyResult]) -> list:
        """[summary]\n
        各並列処理の戻り値をまとめる。\n
        Args:\n
            apply_results ([list]): 各並列処理の戻り値のリスト\n
        Returns:\n
            list: 小ジャンルリンクのリスト\n
        """
        result = []
        for result_list in apply_results:
            try:
                result.append(result_list.get())#TODO:結果の待機時間が長いとTimeOutExceptionが発生する。
            except TimeoutError:
                print("async time out error")
                
        return result
        
            

    def run(self) -> list[list[str]]:
        result = []
        for area in self.area_list:
            result.append(self.__procedure(area))
        result_2d = convert2d_to_1d(result)
        #result_1d = convert2d_to_1d(result_2d)
        return result_2d
            

if __name__ == '__main__':
    freeze_support()
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
    #test = SeleniumMiddlewares(['徳島県'], 4)
    #test.run()
    