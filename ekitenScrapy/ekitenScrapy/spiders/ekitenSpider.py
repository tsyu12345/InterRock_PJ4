from subprocess import call
from typing import Generator, Mapping
from bs4.element import PreformattedString
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import scrapy
import time
import re
from ekitenScrapy.items import EkitenscrapyItem
from multiprocessing import Manager
from ..middlewares import *
from ..JisCode import JisCode
from ..selenium_middleware import SeleniumMiddlewares




def ArrayElementsReplace(array: list, target_str: str, replace_str:str) -> list:
    """[summary]
    配列の要素の指定文字列を指定文字列に置換する。
    Arguments:
        array {list} -- 配列
        target_str {str} -- 置換対象文字列
        replace_str {str} -- 置換文字列
    
    Returns:
        list -- replace_strで置換した配列
    """
    for i in range(len(array)):
        array[i] = array[i].replace(target_str, replace_str)
    return array

def ArrayStrsToOneStr(array:list):
    """[summary]
    配列の要素を一つの文字列にする。
    Arguments:
        array {list} -- 配列
    
    Returns:
        str -- 配列の要素を一つの文字列にする。
    """
    str = ""
    for i in range(len(array)):
        str += array[i] + " "
    return str


class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    #start_urls = ['https://www.ekiten.jp/shop_88106804/']
    MAX_RRTRYCOUNT = 3
    RETEYED = 0
    CRAWLED_URL = []
    
    def __init__(self, prefectures:list, counter, total_count) -> None:
        """
        Summary Lines\n
        初期化処理。対象都道府県とジャンルを指定する。\n
        Args:\n
            prefectures (list): 対象都道府県のリスト\n
            counter (Maneger.Value('i', 0)): 処理済み数を格納する共有メモリ変数\n
            total_count (Maneger.Value('i', 0)): 処理対象数(検索結果数)を格納する共有メモリ変数\n
        """
        self.prefecture_list:list = prefectures 
        self.counter = counter
        self.total_count = total_count
        print("####init####")
        
        
    def start_requests(self):
        """
        Summary Lines
        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
        Yields:
            str: middlewareで返却された小ジャンルURL
        """
        #先に全体の抽出県数を検索。
        for prefecture in self.prefecture_list:
            pref_code = JisCode(prefecture)
            url = 'https://www.ekiten.jp/area/a_prefecture' + str(pref_code) + '/'
            scrapy.Request(url, callback=self.__extraction_shop_result_count, errback=self.error_parse)        
        
        middleware = SeleniumMiddlewares(self.prefecture_list, 4)
        result = middleware.run()
        
        for url in result:
            yield scrapy.Request(url, callback=self.pre_parse, errback=self.error_parse)
     
    def __extraction_shop_result_count(self, response):
        """[summary]\n
        店舗検索の予測総数を取得し、共有メモリの変数に反映する。 \n   
        Args:\n
            response (scrapy.Request): scrapy.Request\n
        """
        counter = response.css('dl.search_result_heading_related_list > div > dd::text').extract_first()
        print(counter)
        self.total_count.value = int(counter)
        
        
    def error_parse(self, failure):
        """Summary Lines
        scrapy.Requestで例外発生時（response.stasusが400、500台）にcallbackする。\n
        一定時間後にリトライリクエストする。\n
        Args:
            failure (scrapy.Request): scrapy.Request
        """
        print("####400 error catch####")
        print("request waiting for 20s")
        if self.RETEYED < self.MAX_RRTRYCOUNT:
            print("RETRYCOUNTER:" + str(self.RETEYED))
            yield scrapy.Request('https://www.google.com/', cllback=None, errback=self.error_parse)
            time.sleep(30)
            response = failure.value.response
            
            self.RETEYED += 1
            return scrapy.Request(
                response.url, 
                callback=self.pre_parse, 
                errback=self.error_parse, 
                dont_filter=True)
    
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
        for elm in response.css('div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            href = elm.css('a::attr(href)').extract_first()
            url = response.urljoin(href)
            if url not in self.CRAWLED_URL:#重複スクレイピング対策
                self.CRAWLED_URL.append(url)
                yield scrapy.Request(url, callback=self.parse, errback=self.error_parse)
                print("call store info scraping..")
        
        #次のページがあるかどうか
        next_page = response.css('div.p-pagination_next > a.button')
        print(next_page)
        if next_page.get() is not None:
            print("#####next page#####")
            next_page_url = response.urljoin(next_page.css('a::attr(href)').extract_first())
            print(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.pre_parse, errback=self.error_parse)
        
            
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
        
        name_elm = response.css('h1.p-shop_header_name > a::text').extract_first()
        item['store_name'] =  name_elm if name_elm is not None else None#店名
        print(item['store_name'])
        
        name_kana_elm = response.css('span.p-shop_header_name_phonetic::text').extract_first()
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
        
        
        item['is_official'] = self.__is_official(response)#公式店かどうか
        print(item['is_official'])
        
        item['evaluation_score'] =  response.css('div.rating_stars_num tooltip > span.tooltip_trigger::text').extract_first()#評価点
        print(item['evaluation_score'])
        
        item['review_count'] = response.css('span.p-shop_header_rating_detail_review_num::text').extract_first() #レビュー件数
        print(item['review_count'])
        
        item['access_info'] = response.xpath('/html/body/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div/span[1]/span/text()').extract_first() #アクセス情報
        print(item['access_info'])
        
        first_junle = response.css('ul.p-shop_header_genre > li > a::text').extract_first()
        print(first_junle)
        item['junle1'] = first_junle if first_junle is not None else None #ジャンル1
        
        other_junle = response.css('ul.p-shop_header_genre > li > span::text').extract()
        for i, junle in enumerate(other_junle):
            if i > 2:
                break
            else:
                item['junle' + str(i+2)] =  junle if junle is not None else None #ジャンル2以降
                print(item['junle' + str(i+2)])
        
        tag_dic = {
            "早朝OK":"can_early_morning",
            "日祝OK":"can_date_celebration",
            "夜間OK":"can_night",
            "駐車場有":"has_park",
            "ネット予約":"can_rev_net",
            "クーポン有":"has_coupon",
            "カード可":"can_card",
            "配達OK":"can_delivery",
        }
        tag_group = response.css('ul.p-shop_header_tag_list.tag_group > li > a::text').extract()
        print(tag_group)
        for tag in tag_group: 
            if tag in tag_dic:
                item[tag_dic[tag]] = "●"
                print(tag_dic[tag] + "●") #各特徴タグの有無
        
        close_station = self.__table_extraction(response, 'アクセス')
        #print(close_station)
        
        item['business_hours'] = self.__extraction_work_time(response)#営業時間
        print(item['business_hours'])
        
        park_info = self.__table_extraction(response, '駐車場')
        item['park_info'] = park_info[0] if len(park_info) > 0 else None #駐車場情報
        print(item['park_info'])
        
        card_info_list = self.__table_extraction(response, 'クレジットカード')
        item['credit_info'] = card_info_list[0] if len(card_info_list) > 0 else None #クレジットカード情報
        print(item['credit_info'])
        
        seat_info_list = self.__table_extraction(response, '座席')
        item['seat_info'] = seat_info_list[0] if len(seat_info_list) > 0 else None #座席情報
        print(item['seat_info'])
        
        use_case_info_list = self.__table_extraction(response, '用途')
        item['use_case'] = use_case_info_list[0] if len(use_case_info_list) > 0 else None #用途情報
        print(item['use_case'])
        
        menu_info_list = self.__table_extraction(response, 'メニュー')
        item['menu'] = menu_info_list[0] if len(menu_info_list) > 0 else None #メニュー
        print(item['menu'])
        
        feature_info_list = self.__table_extraction(response, '特徴')
        item['feature'] = feature_info_list[0] if len(feature_info_list) > 0 else None #特徴
        print(item['feature'])
        
        point_info_list = self.__table_extraction(response, 'ポイント')
        item['point'] = point_info_list[0] if len(point_info_list) > 0 else None #ポイント
        print(item['point'])
        
        here_is_great_info_list = self.__table_extraction(response, 'ここがすごい！')
        item['here_is_great'] = here_is_great_info_list[0] if len(here_is_great_info_list) > 0 else None #ここがすごい！
        print(item['here_is_great'])
        
        media_related_info_list = self.__table_extraction(response, 'メディア関連')
        item['media_related'] = media_related_info_list[0] if len(media_related_info_list) > 0 else None #メディア関連
        print(item['media_related'])
        
        pricing_info_list = self.__table_extraction(response, '価格設定')
        item['pricing'] = pricing_info_list[0] if len(pricing_info_list) > 0 else None #価格設定
        print(item['pricing'])
        
        multi_access_list = self.__table_extraction(response, 'マルチアクセス')
        item['multi_access'] = multi_access_list[0] if len(multi_access_list) > 0 else None #マルチアクセス
        print(item['multi_access']) 
        
        introduction_elm = response.css('div.p-shop_introduction_content.js_toggle_content > div.p-shop_introduction_title::text').extract_first()
        item['introduce'] = introduction_elm if introduction_elm is not None else None #店舗紹介
        print(item['introduce'])
        
        self.counter.value += 1
        """
        scraping items below
        item['store_big_junle'] =  #大ジャンル
        
        item['catch_cp'] =  #キャッチコピー
        item['is_official'] =  #公式店かどうか
        item['evaluation_score'] =  #評価点
        item['review_count'] =  #レビュー件数
        item['image_count'] =  #画像件数
        item['access_info'] =  #アクセス情報
        
        item['latitude'] =  #緯度
        item['longitude'] =  #経度
        item['closest_station'] =  #最寄り駅
       
        
    """
    
    def __extraction_work_time(self, response):
        """[summary]\n
        ヘッダー部分の営業時間を抽出する。
        Args:\n
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト\n
        Returns:\n
            str: 営業時間\n
        """
        head_tag = response.css('div.p-shop_header_access > div.icon_wrapper')
        print(len(head_tag))
        for tag_selector in head_tag:
            menu = tag_selector.css('span.p-shop_header_access_label::text').extract_first()
            if "営業時間" in menu:
                business_time_elm = tag_selector.css('ul > li::text').extract()
                time_list = ArrayElementsReplace(business_time_elm, " ", "")
                time_list = ArrayElementsReplace(time_list, "\n", "")
                business_time = ArrayStrsToOneStr(time_list)
                
                #print(business_time)
                return business_time
               
                
    def __is_official(self, response) ->str:
        """
        [summary]\n 
        公式店か否か判定する。
        Args:\n
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト\n
        Returns:\n
            [str]\n
            公式店:"●"\n
            それ以外:""\n
        """
        offucial_elm = response.css('span.tag_icon official tooltip_trigger').extract_first()
        if offucial_elm is not None:
            return "●"
        else:
            return ""
    
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
                        result_list.append(a.css('a::text').extract_first())
                
                else:
                    result_list.append(elm.css('td::text').extract_first()) 
                    result_list = ArrayElementsReplace(result_list, "\n", "")
                    result_list = ArrayElementsReplace(result_list, "  ", "")

        #print(result_list)
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
        