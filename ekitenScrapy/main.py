from __future__ import annotations
from typing import Any, Optional, Iterator, Final as const
from fileinput import filename
from multiprocessing.managers import SyncManager, ValueProxy

#Scrapy関係のインポート
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 
from RequestTotalCount import RequestTotalCount
from ekitenScrapy.selenium_middleware import SeleniumMiddlewares

#GUI関係のインポート
import PySimpleGUI as gui
from StartUpWindow import StartUpWindow, SelectPrefectureWindow
from RuntimeWindow import RuntimeWindow
import sys
import traceback

#スレッド関係のインポート
from multiprocessing import Manager
import threading as th

#ワークシート関係
from WorkBook import WorkBook, COLUMN_MENUS

#TODO:分散クロールの実装

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
    #TODO:現状のままだと、クローラーを分散させているため、結果が上書きされてしまう。ので、各クローラーごとに別ファイルで一時保存し、それを統合するようにする。
    
    FEED_EXPORT_FIELDS:const[list[str]] = [item_key for item_key in COLUMN_MENUS.keys()]
    
    
    def __init__(self, pref_list:list, save_path:str, junle:str):
        """_summary_\n
        Args:\n
            pref_list(list[str]): 都道府県のリスト\n
            save_path(str): スクレイピング結果の保存先\n
            junle(str): スクレイピングするジャンル -> まだ未実装。\n
        """
        self.pref_list = pref_list
        self.save_path = save_path #最終的な保存先
        
        #Spider settings
        self.settings = get_project_settings()
        self.settings.set('FEED_FORMAT', 'xlsx')
        self.settings.set('FEED_URI', "%(filename).xlsx")
        self.settings.set('FEED_EXPORT_FIELDS', self.FEED_EXPORT_FIELDS)
        self.settings.set('TELNETCONSOLE_ENABLED', False)
        
        #各フラグ、カウンタ変数の定義
        maneger:SyncManager = Manager()
        self.counter:ValueProxy[int] = maneger.Value('i', 0) #現在のクロール済みカウンター
        self.total_counter:ValueProxy[int] = maneger.Value('i', 1) #スクレイピングするサイトの総数
        self.loading_flg:ValueProxy[bool] = maneger.Value('b', False) #ローディング中かどうかのフラグ
        self.end_flg:ValueProxy[bool] = maneger.Value('b', False) #中断のフラグ
        self.progress_num:ValueProxy[int] = maneger.Value('i', 0) #進捗状況の表示用    
        
        #middlewareインスタンスの生成
        self.middleware = SeleniumMiddlewares(self.pref_list, 4, self.progress_num)
        self.crawler = CrawlerProcess(settings=self.settings)
        
        #分散クロール結果の一時保存先を格納したリスト
        self.crawler_temp_save_list:list[str] = []
    
    def __set_crawler_setting(self, crawler_url_list:list[list[str]]) -> None:
        """_summary_\n
        分散クロール用に追加されるクローラーごとに異なる設定のクローラー設定を用意し、Scrapyに予約する。
        """
        for crawler_id, url_list in enumerate(crawler_url_list):
            filename: str = 'crawler_temp_save_' + str(crawler_id)
            self.crawler.crawl(
                'ekitenSpider', 
                self.counter, self.loading_flg, 
                self.end_flg, url_list, 
                comment=None, 
                filename=filename,
            )
            filename = filename +'.xlsx' #拡張子をつけてからリストへ格納。
            self.crawler_temp_save_list.append(filename)
        
    def run(self) -> None:
        """[summary]\n
        GUIの実行ボタンクリック後に実行される。
        Spider一連のスクレイピング処理を実行する。
        このメソッドは非同期で実行されたい。
        """
        #検索総数を取得
        self.loading_flg.value = True
        self.progress_num.value += 1
        count = RequestTotalCount(self.pref_list).get_count()
        print("totalCount: "+str(count))
        self.total_counter.value = count
        result = self.middleware.run()
        print("result: "+str(len(result[0])))
        #result = list_split(4, result)#4つのクローラーで並列できるように分割
        self.progress_num.value += 1
        self.__set_crawler_setting(result)
        self.crawler.start()
        print("crawler exit")
        self.progress_num.value += 1
        self.__save_crawl_result(self.crawler_temp_save_list)
        
    def stop(self):
        self.end_flg.value = True
        
        
    def __save_crawl_result(self, crawl_path_list:list[str]):
        """_summary_\n 
        クロール結果を保存する。
        """
        workbook = WorkBook(self.save_path, crawl_path_list)
        workbook.create_crawl_workbook()
        workbook.col_menulocalize()
        workbook.save()
        
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
        self.running:bool = False
        self.detach:bool = False
        self.complete:bool = False
        
        self.menu_window = StartUpWindow(self.APPLICATION_NAME)
        self.select_pref_window = SelectPrefectureWindow(self.APPLICATION_NAME)
        self.runtime_window = RuntimeWindow(self.APPLICATION_NAME)
        
        self.target_prefecture:list[str] = []
        
        self.crawlar:SpiderCall = SpiderCall([], "", "") #型をつけるため初期化
        self.crawlar_thread:th.Thread = th.Thread(target=self.crawlar.run, daemon=True, args=())
        
    def open_area_select_window(self):
        """_summary_\n
        都道府県選択のサブウィンドウを表示する。
        """
        self.select_pref_window = SelectPrefectureWindow(self.APPLICATION_NAME)
        
        self.select_pref_window.addEventListener(
            self.select_pref_window.OK_BTN_KEY,
            self.close_area_select_window
        )
        
        self.select_pref_window.display()
        
    def close_area_select_window(self):
        """_summary_\n
        都道府県選択のサブウィンドウを閉じ、既定のテキストボックスの表示を更新する。
        """
        self.select_pref_window.dispose()
        textBox_key = self.menu_window.area_select.INPUT_KEY
        self.menu_window.window[textBox_key].update(self.select_pref_window.get_selected_pref_str()) #type: ignore
        
    def __input_check(self):
        """_summary_\n
        実行ボタン押下時に、入力値のフォーマットが正しいかチェックし、違う場合は警告を出す。\n
        Returns:\n
            bool: \n
            すべての入力値のフォーマットが正しい場合->True\n
            上記以外->False\n
        """
        
        checker:list[bool] = [False, False, False]
        
        if self.menu_window.value[self.menu_window.area_select.INPUT_KEY] == "" :#or re.fullmatch('東京都|北海道|(?:京都|大阪)府|.{2,3}県', self.value[self.menu_window.area_select.INPUT_KEY]) == None:
            text2 = "都道府県 ※入力値が不正です。例）東京都, 北海道, 大阪府"
            self.menu_window.window[self.menu_window.area_select.TITLE_KEY].update(text2, text_color='red')#type: ignore
            self.menu_window.window[self.menu_window.area_select.INPUT_KEY].update(background_color='red')
        else:
            text2 = "都道府県"
            self.menu_window.window[self.menu_window.area_select.TITLE_KEY].update(text2, text_color='purple')#type: ignore
            self.menu_window.window[self.menu_window.area_select.INPUT_KEY].update(background_color='white')
            checker[0] = True
            
        if self.menu_window.value[self.menu_window.big_junle_select.JUNLE_BTN_KEY] == "":
            self.menu_window.window[self.menu_window.big_junle_select.TITLE_KEY].update("ジャンル選択 ※選択必須です。", text_color='red')#type: ignore
        else:
            self.menu_window.window[self.menu_window.big_junle_select.TITLE_KEY].update("ジャンル選択", text_color='purple')#type: ignore
            checker[1] = True
            
        if self.menu_window.value[self.menu_window.path_select.INPUT_KEY] == "":
            self.menu_window.window[self.menu_window.path_select.TITLE_KEY].update(
                'フォルダ選択 ※保存先が選択されていません。', #type: ignore
                text_color='red'
            )
            self.menu_window.window[self.menu_window.path_select.INPUT_KEY].update(background_color="red")
        else:
            self.menu_window.window[self.menu_window.path_select.TITLE_KEY].update(text_color='purple')
            self.menu_window.window[self.menu_window.path_select.INPUT_KEY].update(background_color="white")
            checker[2] = True

        if False in checker:
            return False
        else:
            return True
        
    def __crawl_execute(self):
        """_summary_\n
        クローラーを別スレッドで実行する。
        """
        self.target_prefecture = self.menu_window.value[self.menu_window.area_select.INPUT_KEY].split(',')
        self.crawlar = SpiderCall(
            pref_list=self.target_prefecture,
            save_path=self.menu_window.value[self.menu_window.path_select.INPUT_KEY],
            junle=self.menu_window.value[self.menu_window.big_junle_select.JUNLE_BTN_KEY]
        )
        
        self.crawlar_thread:th.Thread = th.Thread(target=self.crawlar.run,args=(), daemon=True)
        self.crawlar_thread.start()
        

        
    def open_runtime_window(self):
        """_summary_\n
        実行中のウィンドウを表示する等、アプリケーションの実行中の制御。
        """
        self.__crawl_execute()
        self.menu_window.dispose()
        
        while self.running:
            total:int = self.crawlar.total_counter.value if self.crawlar.total_counter.value != 0 else 99999
            count:int = self.crawlar.counter.value if self.crawlar.counter.value < total else total - 1
            prog_count:int = self.crawlar.progress_num.value
            #TODO:RuntimeWindowコンポーネントの一部とすること。
            
            #self.runtime_window.display()
            #self.runtime_window.update_progress_bar(prog_count)
            
            progress_bar:Any|bool = gui.OneLineProgressMeter(
                "処理中です.", 
                count, 
                total, 
                '<In Progress>', 
                "現在抽出処理中です。\nこれには数時間かかることがあります。", 
                orientation='h',
            )
            
            if progress_bar is False and self.running:
                self.running = False
                self.detach = True
                self.crawlar.stop()
                break

            if self.crawlar_thread.is_alive() is False:
                self.running = False
                self.complete = True
                break
        
        if self.complete:
            gui.popup_ok(
                "全処理完了しました。保存先を確認してください。\n 保存先:" 
                + self.menu_window.value[self.menu_window.path_select.INPUT_KEY],
                title="完了通知",
                keep_on_top=True
            )
            sys.exit()
            
        if self.detach:
            gui.popup_ok(
                '処理が中断されました',
                title="中断通知",
                keep_on_top=True
            )
            sys.exit()
        
        
        
    
    def exeute_handlar(self):
        """_summary_\n
        実行ボタンクリック時のコールバック関数
        """
        input_ok:bool = self.__input_check()
        if input_ok:
            self.__crawl_execute()
            self.running = True
            self.open_runtime_window()
            
    
    
    def main_menu(self) -> None:
        """[summary]\n
        メインウィンドウを表示し、全体の流れを制御する。
        """
        self.menu_window.addEventListener(
            self.menu_window.area_select.SELECT_BTN_KEY, 
            self.open_area_select_window
        )
        
        self.menu_window.addEventListener(
            self.menu_window.EXECUTE_BTN_KEY,
            self.exeute_handlar
        )
        
        while True:
            
            self.menu_window.display()

            if self.menu_window.event in ("Quit", None):
                self.menu_window.dispose()
                sys.exit()
            
        
#main call
if __name__ == '__main__':
    application = EkitenInfoExtractionApplication()
    application.main_menu()