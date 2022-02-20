from __future__ import annotations
from bs4 import BeautifulSoup as Soup
from ekitenScrapy.JisCode import JisCode
from multiprocessing import Pool, Manager, freeze_support
import requests

def replaceAll(text:str, dic:list[str], replacing_character:str) -> str:
    """[summary]\n
    渡された置換対象文字をすべて１つの文字に置換する。\n
    Args:\n
        text (str): 操作する文字列\n
        dic (list[str, ...]): 置換対象文字のリスト\n
        replacing_character(str): 置換文字\n

    Returns:\n
        str: 置換後の文字列\n
    """
    for i in dic:
        text = text.replace(i, replacing_character)
    return text  

class RequestTotalCount:
    """[summary]\n
        エキテン検索時画面の検索総数を取得する。
    """
    def __init__(self, pref_list: list[str]):
        """[summary]\n
        エキテン検索時画面の検索総数を取得する。
        Args:\n
            pref_list (list): 都道府県のリスト\n
        """
        self.total_counter:int = 0
        self.pref_list:list[str] = pref_list
        self.request_list:list[str] = []
        for area in self.pref_list:
            jis_code = JisCode(area)
            url = 'https://www.ekiten.jp/area/a_prefecture' + str(jis_code) + '/'
            self.request_list.append(url)
    
    def get_count(self) -> int:
        """[summary]\n
        リスト分の都道府県の検索総数を取得し、結果をint型で返す。\n
        Returns:\n
            int: 要求された都道府県分の検索数の合計値\n
        """
        for url in self.request_list:
            response = requests.get(url)
            if response.status_code != 200:
                print('error')
                raise RequestTotalCountError("リクエストに失敗しました。")
            print("statu code :" + str(response.status_code))
            html = response.text
            count = self.__extraction_total(html)
            self.total_counter += count
        
        return self.total_counter
        
    def __extraction_total(self, html) -> int:
        """[summary]\n
        Args:\n
            html(str):ページのhtml
        Returns:\n
            int: そのページ（都道府県）の検索数
        """
        soup = Soup(html, 'html.parser')
        count_elm = soup.select_one('dl.search_result_heading_related_list > div > dd')
        print(count_elm)
        count_str = count_elm.text if count_elm is not None else '0'
        count_str = replaceAll(count_str, ['件', ' ', ','], '')
        count = int(count_str)
        return count

class RequestTotalCountError(Exception):
    """_summary_\n
    ステータスコードが200以外の場合に発生する例外クラス
    """
    pass
    

if __name__ == '__main__':
    test = RequestTotalCount(['徳島県'])
    result = test.get_count()
    print(result)
        