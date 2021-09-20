import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import popup, popup_error
import sys
from scrap import Scrap
#from multiprocessing import Pool
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
    def __init__(self, path, junle, area_list):
        self.path = path
        self.junle = junle
        self.area_list = area_list
        self.scraping = Scrap(path)
        self.scraping.book_init()
        self.url_scrap_flg = False
        self.info_scrap_flg = False
        self.end_flg = False
        self.save_flg = False
        self.sum_cnt = 1#抽出の合計
        self.scrap_cnt = 0#スクレイピング件数

    def __url_search(self):
        #URL scraping
        self.url_scrap_flg = True
        for area in self.area_list:
            self.scraping.search(area)#指定エリアの店舗URLのサーチ
        
    def scrap(self):
        if self.junle == '全ジャンル抽出':
            self.url_scrap_flg = True
            thread = th.Thread(target=self.__url_search)
        thread.start()

        #info scraping 
        scraped_row = 2 #初期値2行目
        readyed_row = 1 #初期値1行目
        self.info_scrap_flg = True
        while self.info_scrap_flg:
            if thread.is_alive != True and self.url_scrap_flg == True:
                #url searchの終了
                self.url_scrap_flg = False
            if self.url_scrap_flg == False and scraped_row == readyed_row:
                #全終了
                self.info_scrap_flg = False
                break 
                
            for row in range(scraped_row, readyed_row+1):
                if self.scraping.sheet.cell(row=row, column=12).value != None:#URL抽出済行
                    if row % 50 == 0:
                        self.scraping.restart()
                    self.scraping.info_scrap(self.scraping.sheet.cell(row=row, column=12).value, row)
                    self.scrap_cnt += 1
                elif self.scraping.sheet.cell(row=row, column=12).value == None: #未検索行
                    scraped_row = row
                    print("for break")
                    break
                scraped_row = readyed_row
                readyed_row = self.scraping.sheet_row
                self.sum_cnt = readyed_row
                
        """
        saving data file and quit webdriver
        """
        self.info_scrap_flg = False
        self.save_flg = True
        self.scraping.book.save(self.path)
        self.scraping.driver.quit()
        self.save_flg = False
        self.end_flg = True
        
        
        """
        self.url_scrap_flg = False
        self.sum_cnt = self.scraping.sheet.max_row
        self.info_scrap_flg = True
        for r in range(2, self.scraping.sheet.max_row+1):
            if r % 50 == 0:
                self.scraping.restart()
            self.scraping.info_scrap(self.scraping.sheet.cell(row=r, column=12).value, r)
            self.scrap_cnt += 1
        """
        

    def cancel(self):
        self.scraping.book.save(self.path)
        self.scraping.driver.quit()    
        self.scraping.book.save(self.path)

if __name__ == "__main__":
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
            job = Job(value['path'], value['Big_junle'], pref_list)
            th1 = th.Thread(target=job.scrap, daemon=True)
            th1.start()
            running = True
            while running:
                if job.info_scrap_flg:
                    run = gui.OneLineProgressMeter("処理中です...", job.scrap_cnt, job.sum_cnt, 'prog', "店舗情報を抽出中です。\nブラウザが複数回再起動します。")
                    if run == False and job.info_scrap_flg:
                        gui.popup_animated('icon_loader_a_bb_01_s1.gif', message="中断処理中...")
                        job.cancel()
                        #pool.terminate()
                        detati = True
                        running = False
                        break
                
                if job.save_flg:
                    gui.popup_animated('icon_loader_a_bb_01_s1.gif', message="最終処理中...")
                
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




