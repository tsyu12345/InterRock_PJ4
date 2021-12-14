from typing import Mapping
from bs4.element import PreformattedString
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import scrapy
import time
import re
from ekitenScrapy.items import EkitenscrapyItem
from ..middlewares import *
from ..JisCode import JisCode
from ..selenium_middleware import SeleniumMiddlewares

class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/shop_79608272/']
    MAX_RRTRYCOUNT = 3
    RETEYED = 0
    """
    def start_requests(self):
        Summary Lines
        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
        Yields:
            str: middlewareで返却された小ジャンルURL
        
        middleware = SeleniumMiddlewares(item['徳島県'], 4)
        result = middleware.run()
        for url in result:
            yield scrapy.Request(url, callback=self.pre_parse, errback=self.error_parse)
    """ 
    def error_parse(self, failure):
        """Summary Lines
        scrapy.Requestで例外発生時（response.stasusが400、500台）にcallbackする。\n
        一定時間後にリトライリクエストする。\n
        Args:
            failure (scrapy.Request): scrapy.Request
        """
        print("####400 error catch####")
        print("request waiting for 20s")
        while self.RETEYED < self.MAX_RRTRYCOUNT:
            time.sleep(20)
            response = failure.value.response
            yield scrapy.Request(
                response.url, 
                callback=self.pre_parse, 
                errback=self.error_parse, 
                dont_filter=True)
            self.RETEYED += 1 
          
    def pre_parse(self, response):
        """Summary Lines
        店舗検索処理。スクレイピング処理をする店舗URLを取得する。
        Args:
            response (scrapy.Request): scrapy.Requestでyieldされたresonseオブジェクト

        Yields:
            scrapy.Request: スクレイピング先URL
        """
        #self.start_urls = self.search(response)
        print(type(response.status))
        self.RETEYED = 0 #成功したらリトライカウントをリセット
        item = EkitenscrapyItem()
        parse_urls = []
        for elm in response.css('div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            href = elm.css('a::attr(href)').extract_first()
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.hon_parse, errback=self.error_parse)
            print("call store info scraping..")
        
        #次のページがあるかどうか
        next_page = response.css('div.p-pagination_next > a.button')
        print(next_page)
        if next_page.get() is not None:
            print("#####next page#####")
            next_page_url = response.urljoin(next_page.css('a::attr(href)').extract_first())
            print(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse, errback=self.error_parse)
        
            
            
    
    def parse(self, response):
        """
        Summary Lines
        本スクレイピング処理。店舗のページにアクセスして情報をitemsに格納する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
        """
        item = EkitenscrapyItem()
        print("#####parse#####")
        #item['store_big_junle'] = response.css('').extract_first() #（保留）大ジャンル
        
        tel_elm:str = response.css('div.p-tel_modal_phone_number_section > p::text').extract()[1]
        item['store_tel'] =  tel_elm.replace('\n', '') if tel_elm is not None else None #電話番号
        print(item['store_tel'])
        
        name_elm = response.css('h1.p-shop_header_name > a::text').extract()[0]
        item['store_name'] =  name_elm if name_elm is not None else None#店名
        print(item['store_name'])
        
        name_kana_elm = response.css('span.p-shop_header_name_phonetic::text').extract()[0]
        item['str_name_kana'] = name_kana_elm if name_kana_elm is not None else None #店名カナ
        print(item['str_name_kana'])
        
        item['price_plan'] =  self.__judgeChargePlan(response)#料金プラン 
        print(item['price_plan'])
        
        address_list = self.__addressSegmentation(response)#住所リスト
        item['pref_code'] = JisCode(address_list[1])#都道府県コード
        print(item['pref_code'])
        item['pref'] = address_list[1]#都道府県
        print(item['pref'])
        item['city'] = address_list[2]#市区町村・番地
        print(item['city'])
        item['full_address'] = address_list[0] #住所
        print(item['full_address'])
        
        url:str = response.request.url
        print(url)
        item['store_link'] = url #scrapingする掲載URL   
        splited_url = url.split('/')
        item['shop_id'] = int(splited_url[3].replace('shop_', ''))#shopID
        print(item['shop_id'])
        
        home_pages = self.__table_extraction(response, 'URL')
        for i, page in enumerate(home_pages):
            if i+1 > 3:
                break
            else:
                item['st_home_page' + str(i+1)] = page
        
        pankuzu_header_div = response.css('div.layout_media.p-topic_path_container > div.layout_media_wide > div.topic_path')
        pan_list = []
        pankuzu_path1:list = pankuzu_header_div.css('a::text').extract()
        for text in pankuzu_path1:
            pan_list.append(text)
        pankuzu_path2:list = pankuzu_header_div.css('em::text').extract()
        for text in pankuzu_path2:
            pan_list.append(text)
        pankuzu_header:str = ""
        for text in pan_list:
            pankuzu_header += text + "/"
        item['pankuzu'] =  pankuzu_header #パンクズヘッダー
        print(item['pankuzu'])
        
        """
        scraping items below
        item['store_big_junle'] =  #大ジャンル
        
        item['catch_cp'] =  #キャッチコピー
        item['is_official'] =  #公式店かどうか
        item['evaluation_score'] =  #評価点
        item['review_count'] =  #レビュー件数
        item['image_count'] =  #画像件数
        item['access_info'] =  #アクセス情報
        item['junle1'] =  #ジャンル1
        item['junle2'] =  #ジャンル2
        item['junle3'] =  #ジャンル3
        item['junle4'] =  #ジャンル4
        item['can_early_morning'] =  #早朝OK
        item['can_date_celebration'] =  #日祝OK
        item['can_night'] =  #夜間OK
        item['has_park'] =  #駐車場あり
        item['can_rev_net'] =  #ネット予約OK
        item['has_coupon'] =  #クーポンあり
        item['can_card'] =  #カード利用OK
        item['can_delivery'] =  #配達OK
        item['latitude'] =  #緯度
        item['longitude'] =  #経度
        item['closest_station'] =  #最寄り駅
        item['business_hours'] =  #営業時間
        item['park_info'] =  #駐車場情報
        item['credit_info'] =  #クレジットカード情報
        item['seat_info'] =  #座席情報
        item['use_case'] =  #用途
        item['menu'] =  #メニュー
        item['feature'] =  #特徴
        item['point'] =  #ポイント
        item['here_is_great'] =  #ここがすごい
        item['media_related'] =  #メディア関連
        item['pricing'] =  #価格設定
        item['multi_acccess'] =  #マルチアクセス
        item['introduce'] =  #紹介文
    """
    
    def __table_extraction(self, response, menu:str) -> list:
        """
        Summary Lines\n
        指定項目のテーブル要素を抽出する\n
        Args:\n
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト\n
            menu (str):抽出したい項目の文字列\n
        Returns:\n
            抽出文字列を格納したリスト[str]\n
        """
        result_list = []
        table_elm = response.css('table.table.p-shop_detail_table.u-mb15 > tbody > tr')
        for elm in table_elm:
            if menu in elm.css('th').extract()[0]:
                
                if menu == 'URL': #URL処理のみ複数考えられるので別処理する。
                    url_elms = elm.css('li.u-fz_s u-mb05 > a')
                    for a in url_elms:
                        result_list.append(a.css('a::text').extract()[0])
                
                else:
                    result_list.append(elm.css('td::text').extract()[0])
        
        return result_list
    
    def __addressSegmentation(self, response) -> list:
        """
        Summary Lines
        住所を分割する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
        Returns:
            分割後の住所を格納したリスト[allAddress, prefecture, municipalities]
        """
        result_list = [None, None, None]
        table_elm = response.css('table.table.p-shop_detail_table.u-mb15 > tbody > tr')
       
        print("#####table_elm#####")
        for elm in table_elm:
            #print(elm.css('tr').get())
            if '住所' in elm.css('th').extract()[0]: #住所の欄を探す
                get_str:str = elm.css('td::text').extract()[0] #住所を取得
                #文字列を整形する
                get_str = get_str.replace('\n', '')
                get_str = get_str.replace('\t', '')
                get_str = get_str.replace('                ', '')
                
                all_address = get_str
                prefecture = re.search(r'東京都|北海道|(?:京都|大阪)府|.{2,3}県', get_str).group()
                splited_address = re.split(r'東京都|北海道|(?:京都|大阪)府|.{2,3}県', get_str)
                municipalities = splited_address[1]
                result_list[0] = all_address
                result_list[1] = prefecture
                result_list[2] = municipalities
        
        return result_list
        
        
    def __judgeChargePlan(self, response) -> str:
        """
        Summary Lines
        料金プランを判定する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
        Returns:
            str: 料金プラン(月額5000円or非会員or無料会員)
        """
        result:str = ""
        near_store_elm = response.css('div.p-area_match_title .heading .lv2').extract_first()
        profile_photo_elm = response.css('div.lazy_load_container').extract_first()
        
        if near_store_elm is None:
            result = "月額5000円"
        elif profile_photo_elm is None:
            result = "非会員"
        else:
            result = "無料会員"
        return result
        