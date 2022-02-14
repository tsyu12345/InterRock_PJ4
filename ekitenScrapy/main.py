from __future__ import annotations

#Scrapy関係のインポート
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 
from RequestTotalCount import RequestTotalCount
import pathlib
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from ekitenScrapy.spiders.ekitenSpider import EkitenspiderSpider
from ekitenScrapy.selenium_middleware import SeleniumMiddlewares

#GUI関係のインポート
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error
import sys
import traceback

#スレッド関係のインポート
from multiprocessing import Pool, freeze_support, Manager
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
        
        
        #Poolオブジェクトの生成
        self.p = Pool(4)
        self.apply_results:list[AsyncResult] = []
    
    def __join(self):
        """Summary Line:\n
        Pool.apply_asyncで実行する関数の終了を待機する

        Returns:\n
            list: Pool.apply_asyncの実行結果、返却値\n
        """
        running = [False, False, False, False]
        return_list = []
        
        while True:
            for i, result in enumerate(self.apply_results):
                if result.ready():
                    return_list.append(result.get())
                    running[i] = True
            if False not in running:
                break
        return return_list
    
    def __make_crawler_process(self, url_2d_list:list[list[str]]) -> None:
        """[summary]\n
        CrawlerProcessのインスタンスを生成し、Poolに登録する。
        """
        for url_list in url_2d_list:
            
            crawler:CrawlerProcess = CrawlerProcess(settings=self.settings)
            crawler.crawl('ekitenSpider', self.counter, self.loading_flg, self.end_flg, url_list)
            async_result = self.p.apply_async(crawler.start, args=())
            self.apply_results.append(async_result)
        

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
        self.__make_crawler_process(crawl_url_list)
        #TODO:ここで各CrawlerProcessの終了を待ち受ける。
        self.__join()
        
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
            text_color="red",
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
        gui.theme('DefaultNoMoreNagging')
        self.width = 700
        self.height = 300
        self.area_menu = AreaSelect()
        self.junle_menu = BigJunleSelect()
        self.path_menu = PathSelect()
        #self.loading_Animation  = LoadingAnimation('icon_loader_a_bb_01_s1.gif','waiting for request...')
        #状態フラグの初期化
        self.runnung = False
        self.detati = False
        self.compleate = False
        #各コンポーネントをフレームにまとめて配置し、windowコンストラクタを生成。
        layout = self.__lay_out()
        self.window = gui.Window(
            'エキテン掲載情報 抽出ツール', 
            layout=layout, 
            icon='1258d548c5548ade5fb2061f64686e40_xxo.ico',
            debugger_enabled=True,
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
    
    def __input_check(self, value):#TODO:self.windowを引数にしているので、これはいらないかも。
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
            checker = self.__input_check(value)
            if checker is True:
                self.__process(value, event)
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