"""_summary_\n
[feature/ImprovementStoreSearch]:店舗検索時間を短縮するため、
以下に、固定値である、各小ジャンルのＵＲＬ接頭辞を辞書型で記載することにする。\n
"""
from __future__ import annotations
from typing import Final as const, Type, TypeVar

class __CATEGORY():
    
    RELAX_BODY_CARE:const = {
        "整体": "cat_seitai",
        "マッサージ": "cat_massage",
        "接骨・整骨": "cat_sekkotsu_seikotsu",
        "鍼灸": "cat_shinkyu",
        "カイロプラクティック": "cat_chiropractic",
        "エステ": "cat_esthetics_salon",
        "健康・美容サービスその他": "cat_health_beauty_other"
    }
    
    HAIR_SALON_NEIL:const = {
        "美容室・ヘアサロン": "cat_hair_salon",
        "理容室・床屋": "cat_barber",
        "ネイルサロン": "cat_nail_salon"
    }
    
    CRAM_SCHOOL: const = {
        "学習塾・塾": "cat_cram_school",
        "予備校": "cat_prep_school",
        "家庭教師": "cat_private_teacher",
        "幼児教室": "cat_infantclassroom"
    }
    
    
    LESSON: const = {
        "英会話教室": "cat_english_school",
        "パソコン教室": "cat_pc_school",
        "料理教室": "cat_cooking",
        "音楽教室": "cat_music_school",
        "ダンススクール": "cat_dance",
        "フラワーアレンジメント教室・生け花スクール": "cat_flower_arrangement",
        "書道・習字": "cat_calligraphy",
        "専門学校・専修学校": "cat_vocational_school",
        "自動車教習所": "cat_driving_school",
        "趣味・スクールその他": "cat_hobby_school_other"
    }
    
    
    DENTISTRY: const = {
        "歯科・歯医者": "cat_dentist",
        "矯正歯科": "cat_orthodontics"
    }
    
    
    HOSPITAL: const = {
        "内科": "cat_internal_medicine",
        "外科": "cat_surgery",
        "小児科": "cat_pediatrics",
        "皮膚科": "cat_dermatology",
        "眼科": "cat_ophthalmology",
        "耳鼻科": "cat_otolaryngology",
        "心療内科": "cat_psychosomatic_medicine",
        "精神科": "cat_psychiatry",
        "産婦人科": "cat_obstetrics_gynecology",
        "美容外科・形成外科": "cat_cosmetic_surgery",
        "整形外科": "cat_orthopedics",
        "人間ドック・検診": "cat_medical_checkup",
        "薬局・ドラッグストア": "cat_drugstore",
        "デイケア・デイサービス・老人ホーム": "cat_dayservice",
        "訪問介護": "cat_homecare",
        "医療その他": "cat_medical_other"
    }
    
    
    GOURMET:const = {
        "和食": "cat_japanese_food",
        "日本料理": "cat_japanese_restaurant",
        "寿司・鮨": "cat_sushi",
        "うなぎ": "cat_eel",
        "天ぷら": "cat_tempura",
        "とんかつ": "cat_pork_cutlet",
        "串揚げ": "cat_kushiage",
        "焼肉・ホルモン": "cat_roast_meat",
        "すき焼き": "cat_sukiyaki",
        "しゃぶしゃぶ": "cat_syabusyabu",
        "焼き鳥": "cat_yakitori",
        "そば・蕎麦": "cat_soba",
        "うどん": "cat_udon",
        "お好み焼き": "cat_okonomiyaki",
        "もんじゃ焼き": "cat_monjayaki",
        "もつ鍋": "cat_motsunabe",
        "中華料理": "cat_chinese_restaurant",
        "ラーメン": "cat_ramen",
        "餃子・ぎょうざ": "cat_dumpling",
        "韓国料理": "cat_korean_restaurant",
        "洋食": "cat_european_food",
        "ステーキ": "cat_steak",
        "ハンバーグ": "cat_hamburg",
        "カレー": "cat_curry",
        "フレンチ・フランス料理": "cat_french_restaurant",
        "イタリアン・イタリア料理": "cat_italian_restaurant",
        "パスタ": "cat_pasta",
        "ピザ": "cat_pizza",
        "ファーストフード": "cat_fastfood",
        "ハンバーガー": "cat_hamburger",
        "レストラン": "cat_restaurant",
        "ファミレス": "cat_family_restaurant",
        "食堂": "cat_messroom",
        "居酒屋": "cat_grogshop",
        "バー": "cat_bar",
        "カフェ・喫茶店": "cat_cafe",
        "パン": "cat_bread",
        "スイーツ・和菓子・洋菓子": "cat_sweets",
        "ケーキ": "cat_cake",
        "グルメその他": "cat_gourmet_other"
    }
    
    
    SHOPPING: const = {
        "デパート・百貨店": "cat_department",
        "スーパーマーケット・食品・食材": "cat_supermarket_food",
        "コンビニ": "cat_convenience",
        "円均一ショップ": "cat_100yen_shop",
        "ホームセンター": "cat_home_center",
        "家電": "cat_consumer_electronic",
        "パソコン": "cat_personal_computer",
        "カメラ": "cat_camera",
        "携帯ショップ": "cat_cellular",
        "服・洋服": "cat_fashion",
        "アクセサリー・ジュエリー": "cat_accessory",
        "靴・シューズ": "cat_shoes",
        "バッグ・鞄": "cat_bag",
        "時計": "cat_watch",
        "メガネ": "cat_glasses",
        "コンタクトレンズ": "cat_contact_glasses",
        "コスメ・化粧品": "cat_cosmetics",
        "家具": "cat_furniture",
        "インテリア": "cat_interior",
        "雑貨": "cat_general_store",
        "文房具・文具": "cat_stationery",
        "印鑑・ハンコ": "cat_seal",
        "書店・本屋": "cat_bookstore",
        "ＣＤ・ＤＶＤレンタル": "cat_dvd_rental",
        "ＣＤ・ＤＶＤ販売": "cat_dvd_sales",
        "楽器": "cat_musical_instrument",
        "玩具・おもちゃ": "cat_toy",
        "スポーツショップ・ゴルフショップ": "cat_sports_shop",
        "自転車": "cat_bicycle",
        "バイク・オートバイ": "cat_bike",
        "ショッピング店その他": "cat_shopping_other"
    }
    
    
    LEISURE:const = {
        "ホテル・ビジネスホテル・旅館": "cat_hotel",
        "旅行会社": "cat_travel_agent",
        "レンタカー": "cat_rental_car",
        "タクシー": "cat_taxi",
        "バス": "cat_bus",
        "遊園地・テーマパーク": "cat_amusement_park",
        "動物園": "cat_zoo",
        "水族館": "cat_aquarium",
        "植物園": "cat_botanical_garden",
        "博物館・美術館": "cat_museum",
        "公園・庭園": "cat_park",
        "キャンプ場・バーベキュー": "cat_camp_site",
        "プール": "cat_pool",
        "道の駅": "cat_roadside_station",
        "映画館": "cat_cinema",
        "劇場": "cat_theater",
        "ゲームセンター・アミューズメントパーク": "cat_game_center",
        "ボウリング場": "cat_bowling",
        "カラオケボックス": "cat_karaoke",
        "マンガ喫茶": "cat_manga_cafe",
        "ネットカフェ": "cat_net_cafe",
        "フィットネスクラブ・スポーツジム": "cat_fitness",
        "スポーツ施設": "cat_sports_facility",
        "ゴルフ場": "cat_golf",
        "銭湯・スーパー銭湯": "cat_public_bath",
        "サウナ": "cat_sauna",
        "お出かけその他": "cat_play_other"
    }
    
    
    RECYCLE: const = {
        "リサイクルショップ": "cat_recycling",
        "金券ショップ・チケットショップ": "cat_ticket",
        "古着": "cat_old_clothes",
        "古本": "cat_book_usedshop",
        "中古ゲーム・CD・DVD": "cat_dvd_usedshop",
        "質屋": "cat_pawnshop",
        "自動車・中古車": "cat_car"
    }
    
    
    PET_ANIMAL: const = {
        "ペットショップ": "cat_pet",
        "ペットサロン・トリミングサロン": "cat_trimmingsalon",
        "ペットホテル": "cat_pethotel",
        "動物病院": "cat_animal_hospital"
    }
    
    
    DELIVERY:const = {
        "花・花屋": "cat_flower",
        "弁当": "cat_box_lunch",
        "デリバリー・宅配・出前": "cat_delivery",
        "酒屋": "cat_liquor_store",
        "クリーニング": "cat_cleaning",
        "家事代行・家政婦": "cat_housekeeping",
        "ベビーシッター": "cat_babysitter",
        "託児所・保育サービス": "cat_nursery",
        "便利屋・代行サービス": "cat_acting_service",
        "家電パソコン修理": "cat_electronics_repair",
        "ハウスクリーニング": "cat_house_cleaning",
        "トイレつまり・水漏れ修理": "cat_water_leak",
        "トイレ・蛇口修理": "cat_equipment_repair",
        "畳・障子・壁紙張り替え": "cat_room_repair",
        "鍵交換・鍵修理": "cat_keyexchange",
        "害虫・害獣駆除": "cat_extermination",
        "庭木剪定・お手入れ": "cat_gardener",
        "宅配便・バイク便・引越し": "cat_delivery_service",
        "倉庫・トランクルーム": "cat_trunk_room",
        "図書館": "cat_library",
        "銀行・金融": "cat_bank",
        "暮らし・生活サービスその他": "cat_living_other"
    }
    
    
    HOME_ESTATE: const = {
        "賃貸不動産": "cat_leased_immovables",
        "不動産売買": "cat_estate_agency",
        "住宅リフォーム": "cat_house_reform"
    }
    
    
    CEREMONIAL: const = {
        "結婚式場": "cat_wedding_hall",
        "結婚相談所": "cat_matrimonial_agency",
        "写真館・フォトスタジオ": "cat_photo_studio",
        "貸し会議室・イベントホール・レンタルスペース": "cat_eventhall",
        "葬儀・葬式": "cat_funeral"
    }

class Genre():
    """_summary_\n
    ジャンルクラス\n
    ジャンル名:{カテゴリ名:接頭辞}
    """
    GENLE_LIST: const[dict[str, dict]] = {
        "リラク・ボディケア":__CATEGORY.RELAX_BODY_CARE,
        "ヘアサロン・ネイル":__CATEGORY.HAIR_SALON_NEIL,
        "学習塾・予備校":__CATEGORY.CRAM_SCHOOL,
        "習い事・スクール":__CATEGORY.LESSON,
        "歯科・矯正歯科":__CATEGORY.DENTISTRY,
        "医院・クリニック・ヘルスケア":__CATEGORY.HOSPITAL,
        "グルメ":__CATEGORY.GOURMET,
        "ショッピング":__CATEGORY.SHOPPING,
        "お出かけ・レジャー":__CATEGORY.LEISURE,
        "リサイクル・中古買取り":__CATEGORY.RECYCLE,
        "ペット・動物":__CATEGORY.PET_ANIMAL,
        "出張デリバリー・生活サービス":__CATEGORY.DELIVERY,
        "住宅・不動産":__CATEGORY.HOME_ESTATE,
        "冠婚葬祭":__CATEGORY.CEREMONIAL
    }
    