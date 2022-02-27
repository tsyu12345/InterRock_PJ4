# -*- coding: utf-8 -*-
from __future__ import annotations
from multiprocessing.managers import ValueProxy

import scrapy
from scrapy.exceptions import CloseSpider
import threading as th
import time
import re
from ekitenScrapy.items import EkitenscrapyItem
from ..middlewares import *
from ..JisCode import JisCode

#TODO:エラーハンドリング。


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
    #start_urls = ['https://www.ekiten.jp/shop_88106804/', 'https://www.ekiten.jp/shop_89135856/', 'https://www.ekiten.jp/shop_42622487/']
    MAX_RRTRYCOUNT = 3
    RETEYED = 0
    CRAWLED_URL = []
    RETRY_URL = []
    
    
    def __init__(self, counter:ValueProxy[int], loading_flg:ValueProxy[bool], end_flg:ValueProxy[bool], small_junle_url_list:list[str]) -> None:
        """
        Summary Lines\n
        初期化処理。selenium_middlewareから受け取ったURLリストに従い、店舗ページをクロールする。\n
        Args:\n
            counter (Maneger.Value('i', 0)): 処理済み数を格納する共有メモリ変数\n
            loading_flg (Manager.Value('b', False)): ローディング中かどうかを格納する共有メモリ変数\n
            end_flg (Manager.Value('b', False)): 中断時のフラグを格納する共有メモリ変数\n
            small_junle_url_list (list): 小ジャンルURLリスト\n
        """ 
        self.counter = counter #type : int
        self.loading_flg = loading_flg #type : bool
        self.end_flg = end_flg #type : bool
        self.small_junle_url_list = small_junle_url_list #type : list[str]
        
        print("####init####")
    
    def __stop_spider(self):
        """
        [summary]\n 
        中断フラグがTrueになるか別スレッドで監視する。
        #このやり方は正直びみょい。
        """
        while True:
            if self.end_flg.value == True:
                #self.middleware.stop()
                raise CloseSpider("spider cancelled")#無理やり例外をスローし終了。


    def start_requests(self):
        """
        Summary Lines
        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
        Yields:
            str: middlewareで返却された小ジャンルURL
        """
        visor = th.Thread(target=self.__stop_spider, daemon=True)
        visor.start()
        
        self.loading_flg.value = True
        
        for url in self.small_junle_url_list:
            yield scrapy.Request(url, callback=self.request_store_page, errback=self.error_process)
        
    def error_process(self, failure):#TODO:ステータスコードが400以上の場合は、リトライする。が、うまくいかない。
        """Summary Lines
        scrapy.Requestで例外発生時（response.stasusが400、500台）にcallbackする。\n
        後にリトライリクエストする。\n
        Args:
            failure (scrapy.Request): scrapy.Request
        """
        self.loading_flg.value = True
        print("####400 error catch####")
        time.sleep(500)#5分ほど待つ
        response = failure.value.response
        url = response.url
        if "shop_" in url:#shop_idが含まれているURLの場合。
            yield scrapy.Request(url, callback=self.parse, errback=self.error_process)
        else:
            yield scrapy.Request(url, callback=self.request_store_page, errback=self.error_process)
        #yield scrapy.Request(url, callback=self.request_store_page, errback=self.error_process)
        #self.RETRY_URL.append(url)
    
    def request_store_page(self, response):
        """Summary Lines
        店舗検索処理。スクレイピング処理をする店舗URLを取得する。
        Args:
            response (scrapy.Request): scrapy.Requestでyieldされたresonseオブジェクト

        Yields:
            scrapy.Request: スクレイピング先URL
        """
        #self.start_urls = self.search(response)
        self.loading_flg.value = True
        print(type(response.status))
        self.RETEYED = 0 #成功したらリトライカウントをリセット
        for elm in response.css('div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            href = elm.css('a::attr(href)').extract_first()
            url = response.urljoin(href)
            if url not in self.CRAWLED_URL:#重複スクレイピング対策
                self.CRAWLED_URL.append(url)
                yield scrapy.Request(url, callback=self.parse, errback=self.error_process)
                print("call store info scraping..")
        
        #次のページがあるかどうか
        next_page = response.css('div.p-pagination_next > a.button')
        print(next_page)
        if next_page.get() is not None:
            print("#####next page#####")
            next_page_url = response.urljoin(next_page.css('a::attr(href)').extract_first())
            print(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.request_store_page, errback=self.error_process)

        
            
    def parse(self, response):
        #TODO:未抽出項目の追加、修正。
        """
        Summary Lines
        本スクレイピング処理。店舗のページにアクセスして情報をitemsに格納する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
        Yields:
            items.ShopItem: 店舗情報を格納するitemオブジェクト
        """
        self.loading_flg.value = False
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
        
        score_elm = response.css('div.layout_media_wide > div.p-shop_header_rating > span.tooltip_trigger::text').extract_first()
        item['evaluation_score'] =  score_elm if score_elm  is not None else None #評価点
        print(item['evaluation_score'])
        
        review_cnt_elm = response.css('div.icon_wrapper > span.icon_wrapper_text > a.js-smooth_scroll_exception_floating::text').extract_first()
        item['review_count'] = review_cnt_elm  if review_cnt_elm is not None else None #レビュー件数
        print(item['review_count'])
        
        img_cnt_elm = response.css('nav.p-shop_detail_nav navigation js_shop_navigation js_floating_target > ul > li.photo > span.p-shop_detail_nav_label_num::text').extract_first()
        item['image_count'] = img_cnt_elm if img_cnt_elm is not None else None #画像件数
        print(item['image_count']) 
        
        access_info_elm = response.css('p-shop_header_access > div.icon_wrapper > span.tooltip p-shop_header_access_root > span.tooltip_trigger::text').extract_first()
        item['access_info'] = access_info_elm if access_info_elm is not None else None #アクセス情報
        print(item['access_info'])
        
        catch_cp_elm = response.css('p-shop_introduction_content js_toggle_content > div.p-shop_introduction_title::text').extract_first()
        item['catch_cp'] = catch_cp_elm if catch_cp_elm is not None else None #キャッチコピー
        print(item['catch_cp'])
        
        item['is_official'] = self.__is_official(response) #公式店舗       
        print(item['is_official'])
        
        yield item
        
        self.counter.value += 1
        
        """
        以下は後日調整。
        scraping items below
        item['store_big_junle'] =  #大ジャンル
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
        offucial_elm = response.css('div.p-shop_header_catch_container > span.tag_icon official tooltip_trigger::text').extract_first()
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
        
        if near_store_elm is not None and profile_photo_elm is None:
            result = "月額5000円"
        elif near_store_elm is None and profile_photo_elm is not None:
            result = "無料会員"
        else:
            result = "非会員"
        """
        if near_store_elm is None:
            result = "月額5000円"
        
        if profile_photo_elm is None:
            result = "非会員"
        else:
            result = "無料会員"
        """
        return result
        