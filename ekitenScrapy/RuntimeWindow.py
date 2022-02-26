from __future__ import annotations
from AbstractGUI import *
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error


class RuntimeWindow(AbsWindowComponent):
    """_summary_\n
    実行中に表示するウィンドウクラス。
    """
    def __init__(self, window_name=None) -> None:
        super().__init__(window_name)
    
    def dispose(self) -> None:
        self.window.close()

    def _lay_out(self) -> list[list[any]]:
        pass
    
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