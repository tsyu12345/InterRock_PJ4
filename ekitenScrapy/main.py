from __future__ import annotations
from multiprocessing.managers import SyncManager, ValueProxy

#Scrapy関係のインポート
import scrapy.item
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 
from RequestTotalCount import RequestTotalCount
from ekitenScrapy.spiders.ekitenSpider import EkitenspiderSpider
from ekitenScrapy.selenium_middleware import SeleniumMiddlewares

#GUI関係のインポート
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error
import sys
import traceback
from guiComponent import *
#スレッド関係のインポート
from multiprocessing import Manager
import threading as th

#ワークシート関係
import ExcelEdit
from ExcelEdit import ExcelEdit as Edit 

#TODO:分散クロールの実装

#Local function

def list_split(n:int, l:list) -> list[list[str]]:
    """Summary Line:\n
    リストを指定数に分割し、その2次元リストを返却する。
    Args:\n
        n (int): 分割数\n
        l (list): 分割対象のリスト\n
    Returns:\n
        list: 分割されたリスト要素を格納したlist\n
    """
    result = []
    for i in range(0, len(l), n):
        add = l[i:i + n]
        result.append(add)
    return result


class SpiderCall: #TODO:中止処理の追加, CrawlerProcessの並列実行
    """
    旧スパイダー実行クラス。現在はRunnerでの構築中。
    Summary:\n
    Spyderを実行する。およびその関連機能の呼び出し、参照を行う。
    Args:\n
        pref_list(list[str]): 都道府県のリスト\n
        save_path(str): スクレイピング結果の保存先\n
        junle(str): スクレイピングするジャンル\n
    """
    #TODO:itemの定義にしたがって、FIELDSの順番、変数名を変更する
    #TODO:twisted.internet.error.CannotListenError: Couldn't listen on 127.0.0.1:6073: [WinError 10048]の修正。
    #↑のエラーが発生するため、Spider実行時エラーが発生している。
    
    FEED_EXPORT_FIELDS:list[str] = [item_key for item_key in ExcelEdit.COLUMN_MENUS.keys()]
    
    def __init__(self, pref_list:list, save_path:str, junle:str):
        
        self.pref_list = pref_list
        self.save_path = save_path
        
        #middlewareインスタンスの生成
        #self.middleware = SeleniumMiddlewares(self.pref_list, 4)
        
        #Spider settings
        self.settings = get_project_settings()
        self.settings.set('FEED_FORMAT', 'xlsx')
        self.settings.set('FEED_URI', save_path)
        self.settings.set('FEED_EXPORT_FIELDS', self.FEED_EXPORT_FIELDS)
        self.settings.set('TELNETCONSOLE_ENABLED', False)
        
        #各フラグ、カウンタ変数の定義
        maneger:SyncManager = Manager()
        self.counter:ValueProxy[int] = maneger.Value('i', 0) #現在の進捗状況のカウンター
        self.total_counter:ValueProxy[int] = maneger.Value('i', 1) #スクレイピングするサイトの総数
        self.loading_flg:ValueProxy[bool] = maneger.Value('b', False) #ローディング中かどうかのフラグ
        self.end_flg:ValueProxy[bool] = maneger.Value('b', False) #中断のフラグ
        
        self.crawler = CrawlerProcess(settings=self.settings)
        
        
    def run(self) -> None:
        """[summary]\n
        GUIの実行ボタンクリック後に実行される。
        Spider一連のスクレイピング処理を実行する。
        このメソッドは非同期で実行されたい。
        """
        #検索総数を取得
        self.loading_flg.value = True
        
        count = RequestTotalCount(self.pref_list).get_count()
        print("totalCount: "+str(count))
        
        self.total_counter.value = count
        
        #result = self.middleware.run()
        #crawl_url_list = list_split(4, result)#4つのクローラーで並列できるように分割
        
        self.crawler.crawl(EkitenspiderSpider, self.counter, self.loading_flg, self.end_flg, [])
        self.crawler.crawl(EkitenspiderSpider, self.counter, self.loading_flg, self.end_flg, [])
        self.crawler.crawl(EkitenspiderSpider, self.counter, self.loading_flg, self.end_flg, [])
        self.crawler.crawl(EkitenspiderSpider, self.counter, self.loading_flg, self.end_flg, [])
        
        self.crawler.start()
        
        self.__finalize()

    def __finalize(self):
        """
        クロール終了後のワークシートの仕上げ処理。各項目の整形
        """
        editor = Edit(self.save_path)
        editor.col_menulocalize()
        editor.save()
        
    def stop(self):
        self.end_flg.value = True
        
class EkitenInfoExtractionApplication(object):
    """
    Summary Line\n
    メインウィンドウを定義する。
    """
    APPLICATION_NAME:str = "エキテン掲載情報スクレイピングツール@"
    
    def __init__(self) -> None:
        #windowの初期化。各コンポーネントの生成。
        gui.theme('DefaultNoMoreNagging')
        self.width:int = 700
        self.height:int = 300
        
        
        #状態フラグの初期化
        self.runnung:bool = False
        self.detati:bool = False
        self.compleate:bool = False
        
        self.menu_window = StartUpWindow(self.APPLICATION_NAME)
        
        self.target_pref_list:list[str] = []
        
    def __process(self, value, event):
        """[summary]\n
        スパイダー呼び出し、スパイダー実行中のプログレスバーを表示。
        """
        pref_list = value['pref_name'].split(",")
        print(pref_list)
        self.running = True
        """各種デーモンスレッドの設定"""
        #spiderの設置
        spider = SpiderCall(pref_list, value['path'], value['Big_junle'])
        spider_process = th.Thread(target=spider.run, args=(), daemon=True)
        #ローディングアニメーション用
        
        #spider実行
        spider_process.start()
        
        while self.running:
            """
            e, v = self.window.read(timeout=10, timeout_key='-timeoutEvent-')
            if e == '-timeoutEvent-' and spider.loading_flg.value:
                loading_gif:gui.Image = self.loading_Animation['loading']
                loading_gif.update_animation([self.loading_Animation.animation_gif], time_between_frames=60)
            else:
                loading_gif:gui.Image = self.loading_Animation['loading']
                loading_gif.update(visible=False)
            """
            
            """ProgressDisplay process"""
            #カウンタ変数の取得
            total:int = spider.total_counter.value if spider.total_counter.value != 0 else 99999
            count:int = spider.counter.value if spider.counter.value < total else total - 1
            #プログレスバーの表示
            progress = gui.OneLineProgressMeter(
                "処理中です.", 
                count, 
                total, 
                '<In Progress>', 
                "現在抽出処理中です。\nこれには数時間かかることがあります。", 
                orientation='h',
            )
            #中断フラグの可否
            if progress is False and self.running:
                self.running = False
                self.detati = True
                self.compleate = True
                spider.stop()
                
                break
                
            
            if spider_process.is_alive() is False:
                self.running = False
                self.compleate = True
                
                break
    
    def __input_check(self, value):
        #TODO:各オブジェクトのkey値変更を反映させる。
        
        checker = [False, False, False]
        
        if value['pref_name'] == "" :#or re.fullmatch('東京都|北海道|(?:京都|大阪)府|.{2,3}県', self.value['pref_name']) == None:
            text2 = "都道府県 ※入力値が不正です。例）東京都, 北海道, 大阪府"
            self.window['pref_title'].update(text2, text_color='red')
            self.window['pref_name'].update(background_color='red')
        else:
            text2 = "都道府県"
            self.window['pref_title'].update(text2, text_color='purple')
            self.window['pref_name'].update(background_color='white')
            checker[0] = True
            
        if value['Big_junle'] == "":
            self.window['junle_title'].update("ジャンル選択 ※選択必須です。", text_color='red')
        else:
            self.window['junle_title'].update("ジャンル選択", text_color='purple')
            checker[1] = True
            
        if value['path'] == "":
            self.window['path_title'].update(
                'フォルダ選択 ※保存先が選択されていません。', text_color='red')
            self.window['path'].update(background_color="red")
        else:
            self.window['path_title'].update(text_color='purple')
            self.window['path'].update(background_color="white")
            checker[2] = True

        if False in checker:
            return False
        else:
            return True
        
    def __compleate_popup(self, value):
        #TODO:GUIコンポーネント関係のソースファイルに移項させる。
        if self.detati:
            gui.popup("処理を中断しました。", title="処理中断")
        else:
            gui.popup("処理が完了しました。\n保存先:" + value['path'], title="処理完了")
    
    
        #TODO:各イベントハンドラーの設定を反映させる。
        """[summary]\n
        ウィンドウで発生したイベントごとの処理を呼び出す。\n
        """
        
        if event == 'エリア選択':
            selected_pref_list = self.pref_select_window.display()
            #windowが閉じると、選択したエリアを集計し返す。
            for i, area in enumerate(selected_pref_list):
                v = area + "," if i != len(selected_pref_list) - 1 else area
                self.window['pref_name'].update(v)

        if event == '抽出実行':
            checker = self.__input_check(value)
            if checker is True:
                self.__process(value, event)
                self.__compleate_popup(value)
            
    def open_pref_select_window(self):
        select_pref_widow = SelectPrefectureWindow(self.APPLICATION_NAME)
        select_pref_widow.addEventListener(select_pref_widow.OK_BTN_KEY, select_pref_widow.dispose)
        select_pref_widow.display()
        = select_pref_widow.selected_pref
        
    def main_menu(self) -> None:
        """[summary]\n
        メインウィンドウを表示し、全体の流れを制御する。
        """
        self.menu_window.addEventListener(
            self.menu_window.area_select.SELECT_BTN_KEY, 
            self.open_pref_select_window,
        )
        
        #TODO:都道府県選択ボタンコンポーネントで、都道府県選択ウィンドウを表示するのをやめる。
        
        
        
        while True:
            
            self.menu_window.display()
            
            if self.menu_window.event in ("Quit", None):
                self.menu_window.dispose()
                break
            
        sys.exit()
            
            
            
        
        
        
#main call
if __name__ == '__main__':
    applicatoin = EkitenInfoExtractionApplication()
    applicatoin.main_menu()