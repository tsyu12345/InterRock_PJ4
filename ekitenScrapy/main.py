#Scrapy関係のインポート
from time import time
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 
from scrapy.statscollectors import StatsCollector
from RequestTotalCount import RequestTotalCount
import pathlib
from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from ekitenScrapy.spiders.ekitenSpider import EkitenspiderSpider

#GUI関係のインポート
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error
import sys
import traceback

#スレッド関係のインポート
from multiprocessing import Pool, freeze_support, Manager
import threading as th

class SpiderExecute:
    """[summary]\n
    CrawlerRunnerでのSpider実行クラス。
    Args:\n
        pref_list(list[str]): 都道府県のリスト\n
        save_path(str): スクレイピング結果の保存先\n
        junle(str): スクレイピングするジャンル\n
    """
    def __init__(self,pref_list:list, save_path:str, junle:str) -> None:
        self.pref_list = pref_list
        
        settings = get_project_settings()
        FEEDS = {
            'items.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': None,
                'indent': 4,
                'item_export_kwargs': {
                'export_empty_fields': True,
                },
            },
            '/home/user/documents/items.xml': {
                'format': 'xml',
                'fields': ['name', 'price'],
                'encoding': 'latin1',
                'indent': 8,
            },
            pathlib.Path(save_path): {
                'format': 'csv',
                'fields': ['price', 'name'],
            },
        }
        #settings.set('FEEDS', save_path)
        #settings.set('FEED_FORMAT', 'csv')
        
        maneger = Manager()
        self.counter = maneger.Value('i', 0) #現在の進捗状況のカウンター
        self.total_counter = maneger.Value('i', 1) #スクレイピングするサイトの総数
        self.loading_flg = maneger.Value('b', False) #ローディング中かどうかのフラグ
        self.end_flg = maneger.Value('b', False) #中断のフラグ
        
        self.runner = CrawlerRunner(settings=None)
    
    def crawl_start(self):
        self.runner.crawl(EkitenspiderSpider(self.pref_list, self.counter, self.total_counter, self.loading_flg, self.end_flg))
        
    def crawl_stop(self):
        r_v = self.runner.stop()
        print(r_v)
        
class SpiderCall: #TODO:中止処理の追加
    """
    旧スパイダー実行クラス！！。現在はRunnnerでの構築中。
    Summary:\n
    Spyderを実行する。およびその関連機能の呼び出し、参照を行う。
    Args:\n
        pref_list(list[str]): 都道府県のリスト\n
        save_path(str): スクレイピング結果の保存先\n
        junle(str): スクレイピングするジャンル\n
    """
    def __init__(self, pref_list:list, save_path:str, junle:str):
        self.pref_list = pref_list
        settings = get_project_settings()
        settings.set('FEED_URI', save_path)
        maneger = Manager()
        self.counter = maneger.Value('i', 0) #現在の進捗状況のカウンター
        self.total_counter = maneger.Value('i', 1) #スクレイピングするサイトの総数
        self.loading_flg = maneger.Value('b', False) #ローディング中かどうかのフラグ
        self.end_flg = maneger.Value('b', False) #中断のフラグ
        self.process = CrawlerProcess(settings)
        self.process.crawl('ekitenSpider', pref_list, self.counter, self.loading_flg, self.end_flg)
        
    def run(self):
        #検索総数を取得
        count = RequestTotalCount(self.pref_list).get_count()
        print("totalCount: "+str(count))
        self.total_counter.value = count
        
        self.process.start() # the script will block here until the crawling is finished

    def stop(self):
        self.end_flg.value = True
        
#GUI claases

class LoadingAnimation:
    """[summary]\n
    クロール待機中や、サーバーブロック発生時の待機期間中にローディングアニメーションを表示させる。\n
    """
    
    def __init__(self,gif_path, msg) -> None:
        self.animation_gif = gif_path 
        self.msg = msg
        self.close_flg = False
        
    def __lay_out(self):
        L = [
            [gui.Image(source=self.animation_gif, key='loading', )],
            [gui.Text(self.msg, key='msg')],
        ]
        return L
        
    def display(self):
        window = gui.Window('リクエスト待機中…', layout=self.__lay_out())
        while True:
            event, value = window.read()
            if self.close_flg:
                break
        window.close()
            

class AreaSelect:
    """
    Summary:\n
    都道府県選択のGUIを表示する。
    """
    def lay_out(self):
        L = [
                [gui.Text("都道府県",
                        key='pref_title', size=(60, None))],
                [gui.InputText(key=('pref_name')), gui.Button('エリア選択')],
            ]
        return L

    def display(self):
        prefs = '北海道,青森県,岩手県,宮城県,秋田県,山形県,福島県,茨城県,栃木県,群馬県,埼玉県,千葉県,東京都,神奈川県,新潟県,富山県,石川県,福井県,山梨県,長野県,岐阜県,静岡県,愛知県,三重県,滋賀県,京都府,大阪府,兵庫県,奈良県,和歌山県,鳥取県,島根県,岡山県,広島県,山口県,徳島県,香川県,愛媛県,高知県,福岡県,佐賀県,長崎県,熊本県,大分県,宮崎県,鹿児島県,沖縄県'
        list_pref = prefs.split(',')
        L = []
        cnt = 0
        for i in range(8):
            add = []
            for j in range(6):
                if cnt != 47:
                    add.append(gui.Checkbox(list_pref[cnt], key=list_pref[cnt]))
                    cnt += 1
            L.append(add)
        L.append([gui.Button('OK', key='OK')])
        window = gui.Window('エリア選択', layout=L)
        pref = []
        while True:
            event, value = window.read()
            print(event)
            print(value)
            for v in value.keys():
                if value[v] == True:
                    pref.append(v)
            if event in ("Quit", None, 'OK'):
                break
        window.close()
        return pref

class BigJunleSelect:
    """
    Summary Line\n 
    ジャンル選択のメニューバー定義。
    """
    def __init__(self):
        self.junle = [
            "全ジャンル抽出",
        ]
        """以下は後日追加予定↓
            "リラク・ボディケア",
            "ヘアサロン・ネイル",
            "学習塾・予備校",
            "習い事・スクール",
            "歯科・矯正歯科",
            "医院・クリニック・ヘルスケア",
            "ショッピング",
            "お出かけ・レジャー",
            "リサイクル・中古買取り",
            "ペット・動物",
            "出張デリバリー・生活サービス",
            "住宅・不動産",
            "冠婚葬祭"
        """

    def lay_out(self):
        L = [
            [gui.Text("抽出ジャンル選択", size=(60, None), key='junle_title')],
            [gui.InputOptionMenu(self.junle, key=("Big_junle"), size=(40, None))]
        ]
        return L

class PathSelect:
    """
    Summary Line\n
    保存先のフォルダ選択を行うGUIボタンの定義。
    """
    def lay_out(self):
        L = [
            [gui.Text("フォルダ選択", key='path_title', size=(60, None))],
            [gui.InputText(key='path'), gui.SaveAs("選択", file_types=( [('CSV (コンマ区切り)','*.csv')]))]
        ]
        return L

class ErrorWindow:
    """[summary]\n
    ハンドルされていない例外が発生したときのエラー画面を表示する。
    """
    def __init__(self, message) -> None:
        """[summary]\n
        Args:\n
            message(str):例外のメッセージ\n
        """
        defaulf_msg = "想定されていないエラーが発生しました。\n開発者に以下のログを転送してください。\n"
        self.msg = defaulf_msg + message #エラーメッセージ全体
    
    def display(self):
        gui.popup_scrolled(
            self.msg, 
            title="Unknown Error",
            size=(40, 20)
        )
        
        
def obj_frame(lay_out_data):
    """[summary]\n
    各オブジェクト群をフレームにして返す。\n
    Args:\n
        lay_out_data (list): \n

    Returns:\n
        list: GUIのレイアウトを返す。\n
    """
    L = [
            [gui.Frame("抽出条件", lay_out_data[0])],
            [gui.Frame("保存先", lay_out_data[1])],
            [gui.Button("抽出実行")]
        ]
    return L

class MainWindow:
    """
    Summary Line\n
    メインウィンドウを定義する。
    """
    def __init__(self) -> None:
        #windowの初期化。各コンポーネントの生成。
        gui.theme('BluePurple')
        self.width = 700
        self.height = 300
        self.area_menu = AreaSelect()
        self.junle_menu = BigJunleSelect()
        self.path_menu = PathSelect()
        self.loading_window = LoadingAnimation(
            'icon_loader_a_bb_01_s1.gif',
            '現在リクエスト待機中です。しばらくお待ちください。'
        )
        #状態フラグの初期化
        self.runnung = False
        self.detati = False
        self.compleate = False
        #各コンポーネントをフレームにまとめて配置し、windowコンストラクタを生成。
        layout = self.__lay_out()
        self.window = gui.Window(
            'エキテン掲載情報 抽出ツール', 
            layout=layout, 
            icon='1258d548c5548ade5fb2061f64686e40_xxo.ico'
        )
    
    def __lay_out(self) -> list:
        area_layout = self.area_menu.lay_out()
        junle_layout = self.junle_menu.lay_out()
        path_layout = self.path_menu.lay_out()
        frame = [
            area_layout[0],area_layout[1],
            junle_layout[0],junle_layout[1],
        ]
        layout = obj_frame([frame, path_layout])
        return layout
    
    def __process(self, value):
        """[summary]\n
        スパイダー呼び出し、スパイダー実行中のプログレスバーを表示。
        """
        pref_list = value['pref_name'].split(",")
        print(pref_list)
        self.running = True
        spider = SpiderCall(pref_list, value['path'], value['Big_junle'])
        spider_process = th.Thread(target=spider.run, args=(), daemon=True)
        spider_process.start()
        while self.running:
            if spider.loading_flg.value:
                self.loading_window.display()
                #gui.popup_animated("c", "ただいま待機中です。\nしばらくお待ちください",time_between_frames=60, keep_on_top=False)
            #ProgressDisplay process
            total:int = spider.total_counter.value if spider.total_counter.value != 0 else 99999
            count:int = spider.counter.value if spider.counter.value < total else total - 1
            
            progress = gui.OneLineProgressMeter(
                "処理中です.", 
                count, 
                total, 
                '<In Progress>', 
                "現在抽出処理中です。\nこれには数時間かかることがあります。", 
                orientation='h',
            )
            
            if progress is False and self.running:
                self.running = False
                self.detati = True
                self.compleate = True
                spider.crawl_stop()
                break
            
            if spider_process.is_alive() is False:
                self.running = False
                self.compleate = True
                break
    
    def __input_check(self, win:gui.Window, value):
        checker = [False, False, False]
        
        if value['pref_name'] == "" :#or re.fullmatch('東京都|北海道|(?:京都|大阪)府|.{2,3}県', self.value['pref_name']) == None:
            text2 = "都道府県 ※入力値が不正です。例）東京都, 北海道, 大阪府"
            win['pref_title'].update(text2, text_color='red')
            win['pref_name'].update(background_color='red')
        else:
            text2 = "都道府県"
            win['pref_title'].update(text2, text_color='purple')
            win['pref_name'].update(background_color='white')
            checker[0] = True
            
        if value['Big_junle'] == "":
            win['junle_title'].update("ジャンル選択 ※選択必須です。", text_color='red')
        else:
            win['junle_title'].update("ジャンル選択", text_color='purple')
            checker[1] = True
            
        if value['path'] == "":
            win['path_title'].update(
                'フォルダ選択 ※保存先が選択されていません。', text_color='red')
            win['path'].update(background_color="red")
        else:
            win['path_title'].update(text_color='purple')
            win['path'].update(background_color="white")
            checker[2] = True

        if False in checker:
            return False
        else:
            return True
        
    def __compleate_popup(self, value):
        if self.detati:
            gui.popup("処理を中断しました。", title="処理中断")
        else:
            gui.popup("処理が完了しました。\n保存先:" + value['path'], title="処理完了")
    
    def __event_listener(self, event, value):
        """[summary]\n
        ウィンドウで発生したイベントごとの処理を呼び出す。\n
        """
        
        if event == 'エリア選択':
            selected_pref_list = self.area_menu.display()
            for i, area in enumerate(selected_pref_list):
                v = area + "," if i != len(selected_pref_list) - 1 else area
                self.window['pref_name'].update(v)

        if event == '抽出実行':
            checker = self.__input_check(self.window, value)
            if checker is True:
                self.__process(value)
                self.__compleate_popup(value)
            
                    
    def display(self) -> None:
        """[summary]\n
        メインウィンドウを表示し、全体の流れを制御する。
        """
        while self.compleate != True:
            try:
                event, value = self.window.read()
                self.__event_listener(event, value) 
                if event in ("Quit", None):#Quit window
                    break
            except:#エラー発生時
                error_log = traceback.format_exc()
                print(error_log)
                popup = ErrorWindow(error_log)
                popup.display()
                break
        
        #終了処理
        self.window.close()
        sys.exit()
        
        
#main call
if __name__ == '__main__':
    window = MainWindow()
    window.display()