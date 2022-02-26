 def __input_check(self, value):
        #TODO:各オブジェクトのkey値変更を反映させる。
        
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