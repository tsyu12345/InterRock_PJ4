#型注釈の有効化
from __future__ import annotations
from typing import Any,  Final as const

#GUI関係のインポート
import PySimpleGUI as gui
from GUI.StartUpWindow import StartUpWindow, SelectPrefectureWindow
from GUI.RuntimeWindow import RuntimeWindow
import sys
#import traceback

#Scrapy
from SpiderModule.SpiderAPI import SpiderCall

#スレッド関係のインポート
from multiprocessing import freeze_support
import threading as th

class EkitenInfoExtractionApplication(object):
    """
    Summary Line\n
    アプリケーション本体のクラスオブジェクト。
    各コンポーネントの呼び出し、実行を行う。
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
        
        self.crawlar: SpiderCall 
        self.crawlar_thread: th.Thread
        
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
    freeze_support()
    application = EkitenInfoExtractionApplication()
    application.main_menu()