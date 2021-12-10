from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import scrapy
import time
from ekitenScrapy.items import EkitenscrapyItem
from ..middlewares import *
from ..JisCode import JisCode
from ..selenium_middleware import SeleniumMiddlewares

class EkitenspiderSpider(scrapy.Spider):
    name = 'ekitenSpider'
    allowed_domains = ['ekiten.jp']
    start_urls = ['https://www.ekiten.jp/area/a_prefecture36/']
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
          
    def parse(self, response):
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
        
            
            
    
    def store_parse(self, response):
        """
        Summary Lines
        本スクレイピング処理。店舗のページにアクセスして情報をitemsに格納する。
        Args:
            response (scrapy.Request): scrapy.Requestで返されたresponseオブジェクト
        """
        item = EkitenscrapyItem()
        print("#####parse#####")
        item['store_big_junle'] = response.css('').extract_first() #（保留）大ジャンル
        tel_elm = response.css('div.p-tel_modal_phone_number_section > p > i.fa fa-phone').get()
        item['store_tel'] =  tel_elm.extract_first() if tel_elm is not None else None #電話番号
        name_elm = response.css('h1.p-shop_header_name').get()
        item['store_name'] =  name_elm.extract_first() if name_elm is not None else None#店名
        
        """
        scraping items below
        item['store_big_junle'] =  #大ジャンル
        item['store_tel'] =  #電話番号
        item['store_name'] =  #店名
        item['str_name_kana'] =  #店名カナ
        item['price_plan'] =  #料金プラン
        item['pref_code'] =  #都道府県コード
        item['pref'] =  #都道府県
        item['city'] =  #市区町村・番地
        item['full_address'] =  #住所
        item['store_link'] =  #scrapingする掲載URL
        item['shop_id'] =  #shopID
        item['st_home_page1'] =  #店舗ホームページ1
        item['st_home_page2'] =  #店舗ホームページ2
        item['st_home_page3'] =  #店舗ホームページ3
        item['pankuzu'] =  #パンクズヘッダー
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