from __future__ import annotations
import os

def ArrayElementsReplace(array: list, target_str: str, replace_str:str) -> list:
    """[summary]
    配列の要素の指定文字列を指定文字列に置換する。
    Arguments:
        array {list} -- 配列
        target_str {str} -- 置換対象文字列
        replace_str {str} -- 置換文字列
    
    Returns:
        list -- replace_strで置換した配列
    """
    for i in range(len(array)):
        array[i] = array[i].replace(target_str, replace_str)
    return array

def ArrayStrsToOneStr(array:list):
    """[summary]
    配列の要素を一つの文字列にする。
    Arguments:
        array {list} -- 配列
    
    Returns:
        str -- 配列の要素を一つの文字列にする。
    """
    str = ""
    for i in range(len(array)):
        str += array[i] + " "
    return str

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

def convert2d_to_1d(l:list) -> list:
    """[summary]
    2次元のリストを1次元に変換する
    Args:
        l (list): 2次元のリスト
    Returns:
        list: 1次元のリスト
    """
    result = []
    for i in range(len(l)):
        for j in range(len(l[i])):
            result.append(l[i][j])
    
    return result
    


def resource_path(relative_path):
    """
    バイナリフィルのパスを提供
    """
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


def process_join(apply_results: list):
    """Summary Line:\n
    Pool.apply_asyncで実行する関数の終了を待機する
    Args:\n
        apply_results (list): Pool.apply_asyncで返却されたリスト\n
    Returns:\n
        list: Pool.apply_asyncの実行結果、返却値\n
    """
    running = [False, False, False, False]
    return_list = []
    
    while True:
        for i, result in enumerate(apply_results):
            if result.ready():
                return_list.append(result.get())
                running[i] = True
        if False not in running:
            break
    return return_list
                
def list_split(n:int, l:list) -> list:
    """Summary Line:\n
    リストを指定数に分割し、そのタプルを返却する。
    Args:\n
        n (int): 分割数\n
        l (list): 分割対象のリスト\n
    Returns:\n
        list: 分割されたリスト要素を格納したlist\n
    """
    result = []
    for i in range(0, len(l), n):
        add = l[i:i + n]
        result.append(add)
    return result