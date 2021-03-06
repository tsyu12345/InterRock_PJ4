# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Callable, Final as const
from multiprocessing.managers import ValueProxy
from unicodedata import category
from scrapy.http import Response

import scrapy
import scrapy.utils.misc
import scrapy.core.scraper
from scrapy.exceptions import CloseSpider

import threading as th
import time
import re
from ekitenScrapy.items import EkitenscrapyItem
from ekitenScrapy.spiders.GenleDef import Genre

from ..JisCode import JisCode
import sys
sys.path.append('../')
from Local import *

#TODO:エラーハンドリング。


def warn_on_generator_with_return_value_stub(spider:scrapy.Spider, callable:Callable):
    """_summary_\n
        [release/ver1.0]:exe起動時に、twisted関係のエラーが発生し、正常にスクレイピングされない。\n
    """
    pass
scrapy.utils.misc.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
scrapy.core.scraper.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub


class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    MAX_RRTRYCOUNT = 3
    RETEYED = 0
    CRAWLED_URL = []
    RETRY_URL = []
    
    
    def __init__(self, counter:ValueProxy[int], loading_flg:ValueProxy[bool], end_flg:ValueProxy[bool], pref_city_strs:list[str],*args:Any, **kwargs:Any) -> None:
        """
        Summary Lines\n
        初期化処理。selenium_middlewareから受け取ったURLリストに従い、店舗ページをクロールする。\n
        Args:\n
            counter (Maneger.Value('i', 0)): 処理済み数を格納する共有メモリ変数\n
            loading_flg (Manager.Value('b', False)): ローディング中かどうかを格納する共有メモリ変数\n
            end_flg (Manager.Value('b', False)): 中断時のフラグを格納する共有メモリ変数\n
            pref_city_str (list[str]): 地域を表す文字列のリスト.[都道府県/市区町村]のフォーマット\n
        """ 
        super().__init__(*args, **kwargs)
        self.counter = counter 
        self.loading_flg = loading_flg 
        self.end_flg = end_flg 
        
        self.pref_city_strs = pref_city_strs
        
        
        
        
    def start_requests(self):
        """
        Summary Lines
        クローリング前処理。city_url_listに格納されたURLに従い、クロール対象カテゴリURLを作成する。
        """
        #終了監視用のスレッドを起動
        visor = th.Thread(target=self.__stop_spider, daemon=True)
        visor.start()
        #ローディングフラグをTrueにする。
        self.loading_flg.value = True
        
    
        urls:const[list[str]] = self.generate_crawl_urls()
        print("CRAWLING URL:", len(urls))
        for url in urls:
            yield scrapy.Request(url, callback=self.request_parse, errback=self.error_process)
        
        
        
    def request_parse(self, response):
        #TODO:指定条件に近いお店以下のタグまで抽出してしまうので、条件を追加する。
        """Summary Lines
        店舗検索処理。スクレイピング処理をする店舗URLを取得する。
        Args:
            response (scrapy.Request): scrapy.Requestでyieldされたresonseオブジェクト

        Yields:
            scrapy.Request: スクレイピング先URL
        """
        #self.start_urls = self.search(response)
        self.loading_flg.value = True
        self.RETEYED = 0 #成功したらリトライカウントをリセット

        store_elms = response.css('div.box.p-shop_box > div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a')
        print("STORE_ELMS:", len(store_elms))
        exlude_storeElms_flag = response.css("h2.heading.border.lv2")
        print(exlude_storeElms_flag)
        if len(exlude_storeElms_flag) != 0:
            store_elms = response.xpath("/html/body/div[@class='l-wrapper']/div/div[@class='l-contents_wrapper']/main/h2[@class='heading border lv2']/preceding-sibling::div/div[@class='layout_media p-shop_box_head']/div[@class='layout_media_wide']/div/h2/a")
            print("EX STORE_ELMS:", len(store_elms))
            
        for elm in store_elms:
            href:str = elm.css('a::attr(href)').extract_first()
            url:str = response.urljoin(href)
            if url not in self.CRAWLED_URL:#重複スクレイピング対策
                self.CRAWLED_URL.append(url)
                print("CRAWLED LEN:", len(self.CRAWLED_URL))
                yield scrapy.Request(url, callback=self.parse, errback=self.error_process)
                print("call store info scraping..")
            
        #次のページがあるかどうか
        next_page = response.css('div.p-pagination_next > a.button')
        print("next page", next_page)
        if next_page.get() is not None:
            print("#####next page#####")
            next_page_url = response.urljoin(next_page.css('a::attr(href)').extract_first())
            print(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.request_parse, errback=self.error_process)
        else:
            print("#####no next page#####")
            yield None
    
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
        
        #item['store_big_junle'] = response.css('').extract_first() #（保留）大ジャンル
        try:
            tel_elm:str | None = response.css('div.p-tel_modal_phone_number_section > p::text').extract()[1]
        except IndexError:
            tel_elm = None
        
        item['store_tel'] =  tel_elm.replace('\n', '') if tel_elm is not None else None #電話番号
                
        name_elm = response.css('h1.p-shop_header_name > a::text').extract_first()
        item['store_name'] =  name_elm if name_elm is not None else None#店名
        
        
        name_kana_elm = response.css('span.p-shop_header_name_phonetic::text').extract_first()
        item['str_name_kana'] = name_kana_elm if name_kana_elm is not None else None #店名カナ
        
        
        item['price_plan'] =  self.__judgeChargePlan(response)#料金プラン 
        
        
        address_list = self.__addressSegmentation(response)#住所リスト
        jis:JisCode = JisCode()
        assert address_list[1] is not None
        item['pref_code'] = jis.get_jis_code(address_list[1])#都道府県コード
        
        
        item['pref'] = address_list[1]#都道府県
        item['city'] = address_list[2]#市区町村・番地
        item['full_address'] = address_list[0] #住所
        
        url:str = response.request.url
        item['store_link'] = url #scrapingする掲載URL   
        splited_url = url.split('/')
        item['shop_id'] = int(splited_url[3].replace('shop_', ''))#shopID
        
        
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
        
        item['is_official'] = self.__is_official(response)#公式店かどうか
        
        item['evaluation_score'] =  response.css('div.rating_stars_num tooltip > span.tooltip_trigger::text').extract_first()#評価点
        
        item['review_count'] = response.css('span.p-shop_header_rating_detail_review_num::text').extract_first() #レビュー件数
        
        item['access_info'] = response.xpath('/html/body/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div/span[1]/span/text()').extract_first() #アクセス情報
        
        first_junle = response.css('ul.p-shop_header_genre > li > a::text').extract_first()
        item['junle1'] = first_junle if first_junle is not None else None #ジャンル1
        
        other_junle = response.css('ul.p-shop_header_genre > li > span::text').extract()
        for i, junle in enumerate(other_junle):
            if i > 2:
                break
            else:
                item['junle' + str(i+2)] =  junle if junle is not None else None #ジャンル2以降
                
        
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

        for tag in tag_group: 
            if tag in tag_dic:
                item[tag_dic[tag]] = "●"
        
        close_station = self.__table_extraction(response, 'アクセス')
        #print(close_station)
        
        item['business_hours'] = self.__extraction_work_time(response)#営業時間
        
        park_info = self.__table_extraction(response, '駐車場')
        item['park_info'] = park_info[0] if len(park_info) > 0 else None #駐車場情報
        
        card_info_list = self.__table_extraction(response, 'クレジットカード')
        item['credit_info'] = card_info_list[0] if len(card_info_list) > 0 else None #クレジットカード情報
        
        seat_info_list = self.__table_extraction(response, '座席')
        item['seat_info'] = seat_info_list[0] if len(seat_info_list) > 0 else None #座席情報
        
        use_case_info_list = self.__table_extraction(response, '用途')
        item['use_case'] = use_case_info_list[0] if len(use_case_info_list) > 0 else None #用途情報
        
        menu_info_list = self.__table_extraction(response, 'メニュー')
        item['menu'] = menu_info_list[0] if len(menu_info_list) > 0 else None #メニュー
        
        feature_info_list = self.__table_extraction(response, '特徴')
        item['feature'] = feature_info_list[0] if len(feature_info_list) > 0 else None #特徴
        
        point_info_list = self.__table_extraction(response, 'ポイント')
        item['point'] = point_info_list[0] if len(point_info_list) > 0 else None #ポイント
        
        here_is_great_info_list = self.__table_extraction(response, 'ここがすごい！')
        item['here_is_great'] = here_is_great_info_list[0] if len(here_is_great_info_list) > 0 else None #ここがすごい！
        
        media_related_info_list = self.__table_extraction(response, 'メディア関連')
        item['media_related'] = media_related_info_list[0] if len(media_related_info_list) > 0 else None #メディア関連
        
        pricing_info_list = self.__table_extraction(response, '価格設定')
        item['pricing'] = pricing_info_list[0] if len(pricing_info_list) > 0 else None #価格設定
        
        multi_access_list = self.__table_extraction(response, 'マルチアクセス')
        item['multi_access'] = multi_access_list[0] if len(multi_access_list) > 0 else None #マルチアクセス
        
        introduction_elm = response.css('div.p-shop_introduction_content.js_toggle_content > div.p-shop_introduction_title::text').extract_first()
        item['introduce'] = introduction_elm if introduction_elm is not None else None #店舗紹介
        
        score_elm = response.css('div.layout_media_wide > div.p-shop_header_rating > span.tooltip_trigger::text').extract_first()
        item['evaluation_score'] =  score_elm if score_elm  is not None else None #評価点
        
        review_cnt_elm = response.css('div.icon_wrapper > span.icon_wrapper_text > a.js-smooth_scroll_exception_floating::text').extract_first()
        item['review_count'] = review_cnt_elm  if review_cnt_elm is not None else None #レビュー件数
        
        img_cnt_elm = response.css('nav.p-shop_detail_nav navigation js_shop_navigation js_floating_target > ul > li.photo > span.p-shop_detail_nav_label_num::text').extract_first()
        item['image_count'] = img_cnt_elm if img_cnt_elm is not None else None #画像件数
        
        access_info_elm = response.css('p-shop_header_access > div.icon_wrapper > span.tooltip p-shop_header_access_root > span.tooltip_trigger::text').extract_first()
        item['access_info'] = access_info_elm if access_info_elm is not None else None #アクセス情報
        
        catch_cp_elm = response.css('p-shop_introduction_content js_toggle_content > div.p-shop_introduction_title::text').extract_first()
        item['catch_cp'] = catch_cp_elm if catch_cp_elm is not None else None #キャッチコピー
        
        item['is_official'] = self.__is_official(response) #公式店舗       
        
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
    ### Private Methods ###

    def __stop_spider(self): #TODO:Public化してmain側APIで呼び出せるようにする。
        """
        [summary]\n 
        中断フラグがTrueになるか別スレッドで監視する。
        #このやり方は正直びみょい。
        """
        while True:
            if self.end_flg.value == True:
                #self.middleware.stop()
                raise CloseSpider("spider cancelled")#無理やり例外をスローし終了。

        
    def error_process(self, failure):#TODO:複数yieldされたとき、403が返された回数分だけ休止処理をしてしまうため効率が激悪い。
        """Summary Lines
        scrapy.Requestで例外発生時（response.stasusが400、500台）にcallbackする。\n
        後にリトライリクエストする。\n
        Args:
            failure (scrapy.Request): scrapy.Request
        """
        #TODO:一度Requestを放ち、その結果でpauseするか判断する。
            # result :403 -> そのままpause
            # result :200 -> 通常のparse, request_parseのやり直し。
        self.loading_flg.value = True
        print("####400 error catch####")
        response: Response = failure.value.response
        
        if response.status == 404:
            print("####404 error catch####")
            return None
        
        yield scrapy.Request(response.url, callback=self.__restart_crawl, errback=self.__crawl_pause)
        
    
    def __crawl_pause(self, response:Response):
        """_summary_\n
        error_processの結果403系でリトライするために呼び出される。\n
        """
        wait_time:int = 400
        print("####403 error catch####")
        print(f"SPIDER STOPING AT{wait_time}sec...")
        self.__temp_pause(wait_time)
        
        yield scrapy.Request(response.url, callback=self.__restart_crawl, errback=self.__crawl_pause)
        print("RESTARTING...")
        
        
    def __temp_pause(self, time_stamp:int = 300) -> None:
        """_summary_\n
        クロールをポーズする。
        Args:
            time_stamp (int) : 待機時間（秒）
            default: 300
        """
        time.sleep(time_stamp)
        
    
    def __restart_crawl(self, response: Response):
        """_summary_\n
        クロールを再開する。
        """
        url: str = response.url
        if "shop_" in url:#shop_idが含まれているURLの場合。
            yield scrapy.Request(url, callback=self.parse, errback=self.error_process)
        else:
            yield scrapy.Request(url, callback=self.request_parse, errback=self.error_process)
    
    
    def __extraction_work_time(self, response) -> str|None:
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
    
    def __table_extraction(self, response, menu:str) -> list[str]:
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
    
    def __addressSegmentation(self, response) -> list[str | None]:
        """
        Summary Lines
        住所を分割する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
        Returns:
            分割後の住所を格納したリスト[allAddress, prefecture, municipalities]
        """
        result_list:list[str | None] = [None, None, None]
        table_elm = response.css('table.table.p-shop_detail_table.u-mb15 > tbody > tr')

        for elm in table_elm:
            #print(elm.css('tr').get())
            if '住所' in elm.css('th').extract()[0]: #住所の欄を探す
                get_str:str = elm.css('td::text').extract()[0] #住所を取得
                #文字列を整形する
                get_str = get_str.replace('\n', '')
                get_str = get_str.replace('\t', '')
                get_str = get_str.replace('                ', '')
                
                all_address = get_str
                
                patten: const[str] = r'東京都|北海道|(?:京都|大阪)府|.{2,3}県'
                re_prefecture = re.search(patten, get_str)
                
                if re_prefecture is not None:
                    prefecture:str = re_prefecture.group() 
                    splited_address = re.split(patten, get_str)
                    municipalities = splited_address[1]
                
                    result_list[0] = all_address #type: ignore
                    result_list[1] = prefecture #type: ignore
                    result_list[2] = municipalities #type: ignore
        
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
    
    
    def generate_crawl_urls(self) -> list[str]:
        """_summary_\n
        市区町村URLを受け取り、カテゴリURLを生成する。\n
        市区町村 > ジャンル > カテゴリページのURL生成\n
        Returns:
            str: カテゴリページクラスのURL
        """
        #city_url_listに格納されたURLに従い、クロール対象カテゴリURLを作成する。
        urls: list[str] = []
        for pref_city_str in self.pref_city_strs:
            
            urls.extend(self.__get_urls(pref_city_str))
            
        return urls
    
    
    def __get_urls(self, area_str: str) -> list[str]:
        """_summary_\n
        1エリアのURLを生成。
        """
        genre_keys: const[list[str]] = list(Genre.GENLE_LIST.keys())
        #genre_keys = ["リラク・ボディケア"] #<- TEST CODE
        urls: list[str] = []
        for key in genre_keys:
            
            categories: const[list[str]] = self.__get_category_strs(key)
            for category in categories:
                #クロール対象URLの生成
                url: const[str] = "https://www.ekiten.jp/" + category + "/" + area_str
                urls.append(url)
        
        return urls

    def __get_category_strs(self, key:str) -> list[str]:
        """_summary_\n
        指定キーのカテゴリの接頭辞のリストを返す。
        Returns:\n
            list[str]\n
        """
        return list(Genre.GENLE_LIST[key].values())