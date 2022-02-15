from __future__ import annotations

#Scrapy関係のインポート
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
    def __init__(self, pref_list:list, save_path:str, junle:str):
        
        self.pref_list = pref_list
        self.save_path = save_path
        
        self.settings = get_project_settings()
        self.settings.set('FEED_FORMAT', 'xlsx')
        self.settings.set('FEED_URI', save_path)
        
        #各フラグ、カウンタ変数の定義
        maneger = Manager()
        self.counter = maneger.Value('i', 0) #現在の進捗状況のカウンター
        self.total_counter = maneger.Value('i', 1) #スクレイピングするサイトの総数
        self.loading_flg = maneger.Value('b', False) #ローディング中かどうかのフラグ
        self.end_flg = maneger.Value('b', False) #中断のフラグ
        
        #middlewareインスタンスの生成
        self.middleware = SeleniumMiddlewares(self.pref_list, 4)

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
        
        result = self.middleware.run()
        crawl_url_list = list_split(4, result)
        
        #スクレイピング処理を実行
        crawler:CrawlerProcess = CrawlerProcess(settings=self.settings)
        for url_list in crawl_url_list:
            crawler.crawl('ekitenSpider', self.counter, self.loading_flg, self.end_flg, url_list)
            
        crawler.start()
        
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
        
#GUI claases

class LoadingAnimation:
    """[summary]\n
    クロール待機中や、サーバーブロック発生時の待機期間中にローディングアニメーションを表示させる。\n
    """
    Y:float = 0.0
    X:float = 60.0
    
    def __init__(self, gif_path:str, msg:str, position:tuple=((X,0),(Y, 0))) -> gui.Window:
        """[summary]\n
        コンストラクタ。\n
        素材のPath,表示位置を指定してインスタンスを生成する。\n
        Args:\n
            gif_path (str): 素材のPath\ns
            msg (str): 表示するメッセージ\n
            position (tuple, optional): 画像表示位置,position:relative;. Defaults to ((X, Y)).\n
            param:X = 50\n
            param:Y = 0\ns
        """
        self.animation_gif = gif_path 
        self.msg = msg
        self.pad = position
        self.window = gui.Window(
            'リクエスト待機中…', 
            layout=self.__lay_out(),
            no_titlebar=False,
        )
        return self.window
        
    def __lay_out(self) -> list:
        """[summary]\n
        レイアウトの定義。\n
        Returns:\n
            list: GUIレイアウトの２次元配列
        """
        L = [
            [gui.Image(key='loading',pad=self.pad, size=(50,50))],
            [gui.Text(self.msg, key='msg')],
        ]
        return L

    def display(self, close_flg:any) -> None:
        """[summary]\n
        ローディングGUIを表示する。\n
        args:\n
            close_flg (ValueProxy[bool]): 中断フラグ\n
        """
        
        #take image element
        img:gui.Image = self.window['loading']
        
        
        event, value = self.window.read(timeout=60)
        img.update_animation([self.animation_gif], 60)
        
        
class EkitenInfoExtractionApplication(object):
    """
    Summary Line\n
    メインウィンドウを定義する。
    """
    def __init__(self) -> None:
        #windowの初期化。各コンポーネントの生成。
        gui.theme('DefaultNoMoreNagging')
        self.width = 700
        self.height = 300
        self.area_menu = AreaSelect()
        self.pref_select_window = SelectPrefectureWindow()
        self.junle_menu = BigJunleSelect()
        self.path_menu = PathSelect()
        
        #状態フラグの初期化
        self.runnung = False
        self.detati = False
        self.compleate = False
        
        layout = StartUpWindowFrame().get_layout()
        
        self.window = gui.Window(
            'エキテン掲載情報 抽出ツール', 
            layout=layout, 
            icon='1258d548c5548ade5fb2061f64686e40_xxo.ico',
            debugger_enabled=True,
        )
    
    
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
    
    def __event_listener(self, event, value):
        #TODO:各イベント処理をコンポーネントのクラス内にバインドする。
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
            
                    
    def main_menu(self) -> None:
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
                popup = ErrorPopup(error_log)
                popup.display()
                break
        
        #終了処理
        self.window.close()
        sys.exit()
        
        
#main call
if __name__ == '__main__':
    applicatoin = EkitenInfoExtractionApplication()
    applicatoin.main_menu()