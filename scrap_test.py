import openpyxl as px 
import PySimpleGUI as gui
import re 
import sys
import os 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
#from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs

class URLScrap():
    book = px.Workbook()
    sheet = book.worksheets[0]
    def __init__(self, path):
        #init WebDriver
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
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        self.path = path
    
    def book_init(self):
        col_list = [
            "エキテン",
            "新規リスト投入日",
            "ジャンル",
            "電話",	
            "店舗名",
            "店舗名カナ",
            "料金プラン",
            "都道府県コード",
            "都道府県",
            "市区町村",
            "番地・建物",
            "住所フル",	
            "店舗URL",
            "shopID",
            "URLその1",
            "URLその2",
            "URLその3",	
            "パンくず",
            "キャッチ",	
            "店舗公式",
            "未確認店舗",
            "評価点数",
            "口コミ数",
            "写真枚数",
            "アクセス",
            "ジャンル1",
            "ジャンル2",
            "ジャンル3",
            "ジャンル4",
            "早朝OK",
            "日祝OK",
            "夜間OK",
            "駐車場有",
            "ネット予約",
            "クーポン有",
            "カード可",
            "出張・宅配あり",
            "緯度",	
            "経度",
            "アクセス／最寄駅",
            "営業時間／定休日",
            "駐車場",
            "クレジットカード",
            "座席",
            "用途",
            "メニュー",
            "特徴",
            "ポイント",
            "ここがすごい！",
        	"メディア関連",
            "価格設定",
            "マルチアクセス",
            "紹介文"
        ]
        for col, menu in enumerate(col_list):
            self.sheet.cell(row=1, column=col+1, value=menu)
        self.book.save(self.path)
    
    def search(self, area):#検索と条件指定
        self.driver.get('https://www.ekiten.jp/')
        sr_box = self.driver.find_element_by_css_selector('#select_form_st_com')
        sr_box.send_keys(area)
        sr_btn = self.driver.find_element_by_css_selector('#js_random_top > div > div > div > form > div > input')
        sr_btn.click()
        actions = ActionChains(self.driver)
        actions.move_to_element(self.driver.find_element_by_css_selector('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > a')).perform()
        #ここから市区町村以下、駅とうの絞り込みを行う
        html = self.driver.page_source
        soup = bs(html, 'lxml')
        selector = 'body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > div.grouped_list_body > ul > li > a'
        city_list = soup.select(selector)
        print(len(city_list))
        print(city_list)
        city_url = self.return_url(city_list, 'https://www.ekiten.jp')
        print(city_url)
        for city in city_url:
            self.driver.get(city)
            station_url = self.extraction_url('#tab_point_0 > div > div > ul > li > a', 'https://www.ekiten.jp')
            for station in station_url:
                self.driver.get(station)
                dist_url = self.extraction_url('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(4) > div > div > div > div > div > ul > li > a', 'https://www.ekiten.jp')
        print(city_url)
        print(station_url)
        print(dist_url)
        """
        while True:
            html = self.driver.page_source
            soup = bs(html, 'lxml')
            try:
                a_tags = soup.select('.p-shop_box_head_title_body > a')
                print(a_tags)
                self.write_url(a_tags)
                next_btn = self.driver.find_element_by_css_selector('div.p-pagination_next > a')
                next_btn.click()
            except NoSuchElementException:
                break
        self.driver.quit()
        """
    def write_url(self, a_tag_list):
        url_list = []
        for a in a_tag_list:
            url_list.append("https://www.ekiten.jp" + a.get('href'))
        for url in url_list:
            row = self.sheet.max_row + 1
            print(row)
            self.sheet.cell(row=row, column=13, value=url)
        self.book.save(self.path)
    
    def extraction_url(self, selector, pre_url):
        html = self.driver.page_source
        soup = bs(html, 'lxml')
        tag_list = soup.select(selector)
        url_list = self.return_url(tag_list, pre_url)    
        return url_list

    def return_url(self, a_tag_list, pre_url):
        url_list = []
        for a in a_tag_list:
            url_list.append(pre_url+a.get('href'))
        return url_list
if __name__ == "__main__":
    scraping = URLScrap('./test.xlsx')
    scraping.book_init()
    scraping.search('徳島県')
    #scraping.scrap()
    scraping.driver.quit()

            



