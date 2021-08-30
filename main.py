import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import popup, popup_error
import sys
from scrap import Scrap
#from multiprocessing import Pool
import threading
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
    def __init__(self, path):
        self.path = path
        self.scraping = Scrap(path)
        self.scraping.book_init()
        self.url_scrap_flg = False
        self.info_scrap_flg = False
        self.end_flg = False
        self.save_flg = False
        self.sum_cnt = 1#抽出中URLの合計
        self.scrap_cnt = 0#スクレイピング件数
    
    """
    def custom_scrap(self, area_list, junle):
        for area in area_list:
            self.driver.get('https://www.ekiten.jp/')
            sr_box = self.driver.find_element_by_css_selector(
                '#select_form_st_com')
            sr_box.send_keys(area)
            sr_btn = self.driver.find_element_by_css_selector(
                '#js_random_top > div > div > div > form > div > input')
            sr_btn.click()
            city_list = self.extraction_url(
                'body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > div.grouped_list_body > ul > li > a', 'https://www.ekiten.jp')

            for city in city_list:
                self.driver.get(city)
                print(city)
                time.sleep(1)
                select = self.driver.find_element_by_css_selector(
                    'body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(3) > div > div > a').text

                # 区町村選択がない場合の処理系
                if select in '駅・バス停から探す ':
                    #junle select and scrap hrere
                # 区町村選択がある場合の処理系
                else:
                    city_list2 = self.extraction_url(
                        'body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(1) > ul > li:nth-child(3) > div > div > div > div > div > ul > li > a', 'https://www.ekiten.jp')
                    for city2 in city_list2:
                        self.driver.get(city2)
                        time.sleep(1)
                        junle_list = self.extraction_url(
                            'body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(2) > ul > li > div > div > div > div > div > ul > li > a', 'https://www.ekiten.jp')
                        print(junle_list)
                        for junle in junle_list:
                            self.driver.get(junle)
                            time.sleep(1)
                            kategoli_list = self.extraction_url('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(2) > ul > li:nth-child(2) > div > div > div > div > div > ul > li > a', 'https://www.ekiten.jp')
                            print(kategoli_list)
                            for kategoli in kategoli_list:
                                self.driver.get(kategoli)
                                self.scrap_url()
                                # scrap URL process here
                            self.restart()
                    self.restart()
                self.restart()
    """
    #def junleselect(self):
        
    def scrap(self, area_list):
        self.url_scrap_flg = True
        for area in area_list:
            self.scraping.search(area)#指定エリアの店舗URLのサーチ
        print("SE OK")
        #self.scraping.deduplication()#重複の削除
        self.url_scrap_flg = False
        self.sum_cnt = self.scraping.sheet.max_row
        self.info_scrap_flg = True
        for r in range(2, self.scraping.sheet.max_row+1):
            if r % 50 == 0:
                self.scraping.restart()
            self.scraping.info_scrap(self.scraping.sheet.cell(row=r, column=12).value, r)
            self.scrap_cnt += 1
        self.info_scrap_flg = False
        self.save_flg = True
        self.scraping.book.save(self.path)
        self.scraping.driver.quit()
        self.save_flg = False
        self.end_flg = True

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
    win = gui.Window('エキテン掲載情報 抽出ツール', layout=layout)
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
            job = Job(path=value['path'])
            #pool = Pool(1)
            #pool.apply_async(job.scrap, args=[pref_list])
            th1 = threading.Thread(target=job.scrap, args=[pref_list], daemon=True)
            th1.start()
            running = True
            while running:
                if job.url_scrap_flg:
                    try:
                        count = job.scraping.sheet.max_row
                    except RuntimeError:
                        pass
                    if count >= job.scraping.result_cnt:
                        count = job.scraping.result_cnt-1
                    #ProgWindowが消えると、detati判定になってしまうため、上限値を超えないように一時的な対策。
                    run = gui.OneLineProgressMeter("処理中です...", count, job.scraping.result_cnt, 'prog', "掲載URLを抽出中です...。\nブラウザが複数回再起動します。", orientation='h')
                    if run == False and job.url_scrap_flg:
                        gui.popup_animated('icon_loader_a_bb_01_s1.gif', message="中断処理中...")
                        job.cancel()
                        #pool.terminate()
                        detati = True
                        running = False
                        break
                           
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




