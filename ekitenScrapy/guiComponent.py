from __future__ import annotations
from AbstractGUI import *
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error
from abc import ABC, ABCMeta, abstractmethod


class AreaSelect(AbsGUIComponent):
    """
    Summary:\n
    都道府県選択をおこなうGUIコンポーネント
    """
    INPUT_KEY = "selected_pref"
    SELECT_BTN_KEY = "select_btn"

    def _lay_out(self):
        L = [
                [gui.Text("都道府県", key='pref_title', size=(60, None))],
                [gui.InputText(key=(self.INPUT_KEY)), gui.Button(self.SELECT_BTN_KEY)],
            ]
        return L
    
    def display_area_select_window(self):
        window = SelectPrefectureWindow()
        window.display()

class SelectPrefectureWindow(AbsWindowComponent):
    """[summary]\n
    別ウィンドウで表示する、都道府県選択のGUIコンポーネント。
    """
    OK_BTN_KEY:str = 'OK'
    upper_row:int = 8
    upper_col:int = 6
    
    def __init__(self) -> None:
        self.event_handler:dict = {
            self.OK_BTN_KEY: self.__save_selected_pref,
        }
        
        pref_str:str = '北海道,青森県,岩手県,宮城県,秋田県,山形県,福島県,茨城県,栃木県,群馬県,埼玉県,千葉県,東京都,神奈川県,新潟県,富山県,石川県,福井県,山梨県,長野県,岐阜県,静岡県,愛知県,三重県,滋賀県,京都府,大阪府,兵庫県,奈良県,和歌山県,鳥取県,島根県,岡山県,広島県,山口県,徳島県,香川県,愛媛県,高知県,福岡県,佐賀県,長崎県,熊本県,大分県,宮崎県,鹿児島県,沖縄県'
        self.prefecture_list:list[str] = pref_str.split(',')
        
        self.window = gui.Window('エリア選択', layout=self._lay_out()) #Windowインスタンス
        self.selected_pref:list[str] = []
        
    
    def _lay_out(self) -> list:
        
        L:list = []
        index = 0
        for i in range(self.upper_row):
            add = []
            for j in range(self.upper_col):
                if index != 47:
                    add.append(gui.Checkbox(self.prefecture_list[index], key=self.prefecture_list[index]))
                    index += 1
            L.append(add)
        
        L.append([gui.Button('OK', key=self.OK_BTN_KEY)])
        return L
    
    def __save_selected_pref(self, value:dict) -> None:
        """
        選択された都道府県を保存する。
        """
        for v in value.keys():
            if value[v] == True and v not in self.selected_pref:
                self.selected_pref.append(v)
    
    def display(self) -> list[str]:
        
        while True:
            event, value = self.window.read()
            self.event_handler[event](value)
            if event in ("Quit", None, 'OK'):
                break
        self.window.close()
        return self.selected_pref
        
class BigJunleSelect(AbsGUIComponent):
    """
    Summary Line\n 
    ジャンル選択のメニューバー定義。
    """
    JUNLE_BTN_KEY:str = "Big_junle"
    
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
        
    def _lay_out(self):
        L = [
            [gui.Text("抽出ジャンル選択", size=(60, None), key='junle_title')],
            [gui.InputCombo(self.junle, key=(self.JUNLE_BTN_KEY), size=(40, None))]
        ]
        return L
    
class PathSelect(AbsGUIComponent):
    """
    Summary Line\n
    保存先のフォルダ選択を行うGUIボタンの定義。
    """
    INPUT_KEY:str = "Path"
    
    def _lay_out(self) -> list[list[gui.Text], list[gui.InputText, gui.Button]]:
        L = [
            [gui.Text("フォルダ選択", key='path_title', size=(60, None))],
            [gui.InputText(key=self.INPUT_KEY), gui.SaveAs("選択", file_types=( [('Excelファイル','*.xlsx')]))]
        ]
        return L

class RuntimeWindow(AbsWindowComponent):
    """_summary_\n
    実行中に表示するウィンドウクラス。
    """
    pass

class StartUpWindow(AbsWindowComponent):
    """[summary]\n
    初期設定画面のGUI画面の定義。
    """
    #TODO:現在暗黙的にコンポーネント内のlayout配列の要素数が2であることを前提としているのでこれを直す。
    
    EXECUTE_BTN_KEY:str = "execute"
    
    def __init__(self) -> None:
        self.area_select:AreaSelect = AreaSelect()
        self.big_junle_select:BigJunleSelect = BigJunleSelect()
        self.path_select:PathSelect = PathSelect()
        
        self.layout = self._lay_out()
        self.window = gui.Window(
            'エキテン掲載情報 抽出ツール', 
            layout=self.layout,
            icon='1258d548c5548ade5fb2061f64686e40_xxo.ico',
            debugger_enabled=True,
        )
        
        #状態変数の初期化。
        self.active:bool = True
        self.deactivate:bool = False
        
        self.value:dict = {}
        self.event:str = None
        
    
    def _lay_out(self) -> list:
        
        area_layout = self.area_select._lay_out()
        junle_layout = self.big_junle_select._lay_out()
        path_layout = self.path_select._lay_out()
        
        L = [
                [
                    gui.Frame(
                        "抽出条件", [
                            area_layout[0], area_layout[1],
                            junle_layout[0], junle_layout[1],   
                        ]
                    )
                ],
                [
                    gui.Frame(
                        "保存先",
                        [path_layout[0], path_layout[1]],
                    )
                ],
                [
                    gui.Button("抽出実行", key=self.EXECUTE_BTN_KEY),
                ]
            ]
        
        return L
    
    def __event_listener(self, key:str, callback:callable) -> None:
        #TODO:callback関数に引数を渡せるようにする。
        """
        [summary]\n
        イベントリスナーを設定する。\n
        Args:\n
            key: イベントキー\n
            callback: イベントハンドラー\n
        """
        if self.event == key:
            callback()
        
        
        
    
    def display(self) -> None:
        self.event, self.value = self.window.read()
        
    def dispose(self) -> None:
        self.window.close()
    
    

class LoadingAnimation(AbsGUIComponent):
    """_summary_\n
    ローディングアニメーションを表示するGUIコンポーネント。
    未実装。
    Args:
        AbsGUIComponent (_type_): _description_
    """
    def __init__(self, msg:str, size:tuple[int, int], source_path:str) -> None:
        self.msg = msg
        self.width = size[0]
        self.height = size[1]
        self.source_path = source_path
        
    def _lay_out(self) -> list[list[any]]:
        
        L:list[list[any]] = [
            []
        ]
        
        return L

"""
class LogOutputWindow(AbsGUIComponent):
    
    def __init__(self):
"""     

class ErrorPopup():
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