from __future__ import annotations

import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error
from abc import ABC, ABCMeta, abstractmethod

class AbsGUIComponent(object, metaclass=ABCMeta):
    """[summary]\n
    各GUIコンポーネントの基底抽象クラス定義。
    """
    
    @abstractmethod
    def _lay_out(self) -> list:
        """
        protectedメソッド。
        GUIコンポーネントのレイアウト配列を返す。
        """
        pass

class AreaSelect(AbsGUIComponent):
    """
    Summary:\n
    都道府県選択をおこなうGUIコンポーネント
    """
    
    def __init__(self) -> None:
        pref_str:str = '北海道,青森県,岩手県,宮城県,秋田県,山形県,福島県,茨城県,栃木県,群馬県,埼玉県,千葉県,東京都,神奈川県,新潟県,富山県,石川県,福井県,山梨県,長野県,岐阜県,静岡県,愛知県,三重県,滋賀県,京都府,大阪府,兵庫県,奈良県,和歌山県,鳥取県,島根県,岡山県,広島県,山口県,徳島県,香川県,愛媛県,高知県,福岡県,佐賀県,長崎県,熊本県,大分県,宮崎県,鹿児島県,沖縄県'
        self.prefecture_list:list = pref_str.split(',')
        
    
    def _lay_out(self):
        L = [
                [gui.Text("都道府県", key='pref_title', size=(60, None))],
                [gui.InputText(key=('pref_name')), gui.Button('エリア選択')],
            ]
        return L

    
class SelectPrefectureWindow(AbsGUIComponent):
    """[summary]\n
    別ウィンドウで表示する、都道府県選択のGUIコンポーネント。
    """
    
    def __init__(self) -> None:
        self.display_row:int = 8 #表示可能行数
        self.display_col:int = 6 #表示可能列数
        
        pref_str:str = '北海道,青森県,岩手県,宮城県,秋田県,山形県,福島県,茨城県,栃木県,群馬県,埼玉県,千葉県,東京都,神奈川県,新潟県,富山県,石川県,福井県,山梨県,長野県,岐阜県,静岡県,愛知県,三重県,滋賀県,京都府,大阪府,兵庫県,奈良県,和歌山県,鳥取県,島根県,岡山県,広島県,山口県,徳島県,香川県,愛媛県,高知県,福岡県,佐賀県,長崎県,熊本県,大分県,宮崎県,鹿児島県,沖縄県'
        self.prefecture_list:list[str] = pref_str.split(',')
        
        self.window = gui.Window('エリア選択', layout=self._lay_out()) #Windowインスタンス
        self.selected_pref:list[str] = []
        
    
    def _lay_out(self) -> list:
        
        L:list = []
        index = 0
        for i in range(self.display_row):
            add = []
            for j in range(self.display_col):
                if index != 47:
                    add.append(gui.Checkbox(self.prefecture_list[index], key=self.prefecture_list[index]))
                    index += 1
            L.append(add)
        
        L.append([gui.Button('OK', key='OK')])
        return L
    
    def display(self) -> list[str]:
        
        while True:
            event, value = self.window.read()
            print(event)
            print(value)
            for v in value.keys():
                if value[v] == True and v not in self.selected_pref:
                    self.selected_pref.append(v)
            if event in ("Quit", None, 'OK'):
                break
        self.window.close()
        return self.selected_pref
        
class BigJunleSelect(AbsGUIComponent):
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
        
    def _lay_out(self):
        L = [
            [gui.Text("抽出ジャンル選択", size=(60, None), key='junle_title')],
            [gui.InputCombo(self.junle, key=("Big_junle"), size=(40, None))]
        ]
        return L
    
class PathSelect(AbsGUIComponent):
    """
    Summary Line\n
    保存先のフォルダ選択を行うGUIボタンの定義。
    """
    def _lay_out(self):
        L = [
            [gui.Text("フォルダ選択", key='path_title', size=(60, None))],
            [gui.InputText(key='path'), gui.SaveAs("選択", file_types=( [('Excelファイル','*.xlsx')]))]
        ]
        return L


class StartUpWindowFrame(AbsGUIComponent):
    """[summary]\n
    初期設定画面のGUI画面の定義。各種GUIコンポーネントを組み合わせている。
    """
    #TODO:現在暗黙的にコンポーネント内のlayout配列の要素数が2であることを前提としているのでこれを直す。
    
    def __init__(self) -> None:
        self.area_menu = AreaSelect()
        self.junle_menu = BigJunleSelect()
        self.path_menu = PathSelect()
    
    def _lay_out(self) -> list:
        
        area_layout = self.area_menu._lay_out()
        junle_layout = self.junle_menu._lay_out()
        path_layout = self.path_menu._lay_out()
        
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
                    gui.Button("抽出実行")
                ]
            ]
        
        return L
    
    def get_layout(self) -> list:
        """[summary]\n
        画面のレイアウトを返す。
        """
        return self._lay_out()
        
        


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