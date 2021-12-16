# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EkitenscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
    結果出力用Item、ワークシートに書き出すItemを定義。
    """
    store_big_junle = scrapy.Field() #大ジャンル
    store_tel = scrapy.Field() #電話番号
    store_name = scrapy.Field() #店名
    str_name_kana = scrapy.Field() #店名カナ
    price_plan = scrapy.Field() #料金プラン
    pref_code = scrapy.Field() #都道府県コード
    pref = scrapy.Field() #都道府県
    city = scrapy.Field() #市区町村・番地
    full_address = scrapy.Field() #住所
    store_link = scrapy.Field() #scrapingする掲載URL
    shop_id = scrapy.Field() #shopID
    st_home_page1 = scrapy.Field() #店舗ホームページ1
    st_home_page2 = scrapy.Field() #店舗ホームページ2
    st_home_page3 = scrapy.Field() #店舗ホームページ3
    pankuzu = scrapy.Field() #パンクズヘッダー
    catch_cp = scrapy.Field() #キャッチコピー
    is_official = scrapy.Field() #公式店かどうか
    evaluation_score = scrapy.Field() #評価点
    review_count = scrapy.Field() #レビュー件数
    image_count = scrapy.Field() #画像件数
    access_info = scrapy.Field() #アクセス情報
    junle1 = scrapy.Field() #ジャンル1
    junle2 = scrapy.Field() #ジャンル2
    junle3 = scrapy.Field() #ジャンル3
    junle4 = scrapy.Field() #ジャンル4
    can_early_morning = scrapy.Field() #早朝OK
    can_date_celebration = scrapy.Field() #日祝OK
    can_night = scrapy.Field() #夜間OK
    has_park = scrapy.Field() #駐車場あり
    can_rev_net = scrapy.Field() #ネット予約OK
    has_coupon = scrapy.Field() #クーポンあり
    can_card = scrapy.Field() #カード利用OK
    can_delivery = scrapy.Field() #配達OK
    latitude = scrapy.Field() #緯度
    longitude = scrapy.Field() #経度
    closest_station = scrapy.Field() #最寄り駅
    business_hours = scrapy.Field() #営業時間
    park_info = scrapy.Field() #駐車場情報
    credit_info = scrapy.Field() #クレジットカード情報
    seat_info = scrapy.Field() #座席情報
    use_case = scrapy.Field() #用途
    menu = scrapy.Field() #メニュー
    feature = scrapy.Field() #特徴
    point = scrapy.Field() #ポイント
    here_is_great = scrapy.Field() #ここがすごい
    media_related = scrapy.Field() #メディア関連
    pricing = scrapy.Field() #価格設定
    multi_access = scrapy.Field() #マルチアクセス
    introduce = scrapy.Field() #紹介文
    
    



