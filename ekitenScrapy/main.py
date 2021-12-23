#Scrapy関係のインポート
from scrapy.crawler import CrawlerProcess 
from scrapy.utils.project import get_project_settings 

#GUI関係のインポート
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error
import sys
from multiprocessing import Pool, freeze_support
import threading as th

class SpiderCall:
    """
    Summary:\n
    Spyderを実行する。およびその関連機能の呼び出し、参照を行う。
    """
    def __init__(self, pref_list:list):
        settings = get_project_settings()
        settings.set('FEED_URI', 'results_TEST.csv')
        self.process = CrawlerProcess(get_project_settings())
        self.process.crawl('ekitenSpider', prefectures=pref_list)
        
    def run(self):
        self.process.start() # the script will block here until the crawling is finished
    

#GUI claases
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
            [gui.Text("抽出ジャンル選択", size=(60, None))],
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
            [gui.InputText(key='path'), gui.SaveAs("選択", file_types=( [('Excelファイル','*.xlsx')]))]
        ]
        return L

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
        gui.theme('BluePurple')
        self.width = 700
        self.height = 300
        self.area_menu = AreaSelect()
        self.junle_menu = BigJunleSelect()
        self.path_menu = PathSelect()
        self.runnung = False
        self.detati = False
        self.compleate = False
        layout = self.__lay_out()
        self.window = gui.Window(
            'エキテン掲載情報 抽出ツール', 
            layout=layout, 
            icon='../../1258d548c5548ade5fb2061f64686e40_xxo.ico'
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
    
    def __event_listener(self, event, value):
        if event == 'エリア選択':
            """
            選択されたエリアを取得し、結果を表示する。
            """
            selected_pref_list = self.area_menu.display()
            display_area = ""
            for area in selected_pref_list:
                display_area += area + ","
            self.window['pref_name'].update(display_area)

        if event == '抽出実行':
            pass 
            #process here when event is '抽出実行'
            
    def display(self):
        while self.compleate != True:
            event, value = self.window.read()
            self.__event_listener(event, value) 
            
        
        
        
        
#main call
if __name__ == '__main__':