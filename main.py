import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, popup, popup_error
import sys
from multiprocessing import Pool, freeze_support
from scraping import Implementation
import threading as th
class AreaSelect:
    def lay_out(self):
        L = [
                [gui.Text("都道府県",
                        key='pref_title', size=(60, None))],
                [gui.InputText(key=('pref_name')), gui.Button('エリア選択')],
            ]
        return L

    def area_select(self):
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

    def __init__(self):
        self.junle = [
            "全ジャンル抽出",
        ]
        """
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
    def lay_out(self):
        L = [
            [gui.Text("フォルダ選択", key='path_title', size=(60, None))],
            [gui.InputText(key='path'), gui.SaveAs("選択", file_types=( [('Excelファイル','*.xlsx')]))]
        ]
        return L

def obj_frame(lay_out_data):
    L = [
            [gui.Frame("抽出条件", lay_out_data[0])],
            [gui.Frame("保存先", lay_out_data[1])],
            [gui.Button("抽出実行")]
        ]
    return L

class Job():
    def __init__(self, path, area_list, junle):
        self.path = path
        self.area_list = area_list
        self.junle = junle
        self.scrap = Implementation(self.path, self.area_list, self.junle)
        self.url_scrap_flg = False
        self.info_scrap_flg = False
        self.scrap_cnt = 0 #info_scrap count
        self.scrap_sum = 1 #sum count of scraiping
        self.check_flg = False
        self.end_flg = False
        self.detati_flg = False
        self.exception_flg = False
        
    def run(self):
        """
        scraping.py呼び出しメソッド
        """    
        self.info_scrap_flg = True
        self.scrap.run()
        self.info_scrap_flg = False
        self.end_flg = True


if __name__ == "__main__":
    freeze_support()
    gui.theme('BluePurple')
    width = 700
    height = 300
    area_obj = AreaSelect()
    big_junle_obj = BigJunleSelect()
    path_obj = PathSelect()
    area_select = area_obj.lay_out()
    big_junle_slc = big_junle_obj.lay_out()
    frame1 = [
        area_select[0],area_select[1],
        big_junle_slc[0], big_junle_slc[1],    
    ]
    layout = obj_frame([frame1, path_obj.lay_out()])
    win = gui.Window('エキテン掲載情報 抽出ツール', layout=layout, icon='1258d548c5548ade5fb2061f64686e40_xxo.ico')
    comp_flg = False
    running = False
    detati = False
    while comp_flg == False:
        event, value = win.read()
        print(event)
        print(value)
        if event == 'エリア選択':
            pref_list = area_obj.area_select()
            add = ""
            for i in range(len(pref_list)):
                if i == len(pref_list)-1:
                    add += pref_list[i]
                else:
                    add += pref_list[i] + ","
                win['pref_name'].update(add)
        
        if event == '抽出実行':
            pref_list = value['pref_name'].split(",")
            print(pref_list)
            job = Job(value['path'], pref_list, value['Big_junle'])
            th1 = th.Thread(target=job.run, daemon=True)
            th1.start()
            running = True
            while running:
                counters = job.scrap.call_counter_value()
                done_count = counters[0]
                sum_count = counters[1]
                if done_count >= sum_count:
                    done_count -= 1
                if sum_count == 0:
                    sum_count = 1

                if job.info_scrap_flg:
                    run = gui.OneLineProgressMeter("処理中です...", done_count, sum_count, 'prg',"店舗情報を抽出中です。\nブラウザが複数回再起動します。")
                    if run == False and job.info_scrap_flg:
                        gui.popup_animated('icon_loader_a_bb_01_s1.gif', message="中断処理中...")
                        job.scrap.cancel()
                        #pool.terminate()
                        detati = True
                        running = False
                        break
                
                if job.end_flg:
                    running = False
                    comp_flg = True
                    #pool.close()
                    break
        # when window close
        if detati:
            gui.popup('処理を中断しました。ファイルを確認してください。\n保存先：'+ job.path, keep_on_top=True)
            comp_flg = True
            break
        if comp_flg:
            gui.popup('お疲れ様でした。抽出完了です。ファイルを確認してください。\n保存先：'+ job.path, keep_on_top=True)
            break

        if event in ("Quit", None):
            break
    
    win.close()
    sys.exit()