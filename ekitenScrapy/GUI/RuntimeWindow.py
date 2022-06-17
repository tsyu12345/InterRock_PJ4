from __future__ import annotations
from .AbstractGUI import *
import PySimpleGUI as gui
from PySimpleGUI.PySimpleGUI import T, Window, popup, popup_error


class RuntimeWindow(AbsWindowComponent):
    """_summary_\n
    実行中に表示するウィンドウクラス。
    """
    ProcessNumber:int = 5
    CUSTOM_WINDOW_NAME:str = '実行中…'
    PROG_BAR_KEY:str = "prog_bar"
    
    def __init__(self, window_name=None) -> None:
        super().__init__(window_name)
        self.window = gui.Window(
            window_name + self.CUSTOM_WINDOW_NAME,
            layout=self._lay_out(),
        )
    
    def dispose(self) -> None:
        self.window.close()

    def _lay_out(self) -> list[list[any]]:
        L:list[list[any]] = [
            [gui.Text("実行中", size=(60, None))],
            [gui.ProgressBar(key=self.PROG_BAR_KEY, orientation='h', max_value=self.ProcessNumber, size=(40, 40))],
        ]
        return L
    
    def update_progress_bar(self, now_process_count:int) -> None:
        """_summary_\n
        プログレスバーの表示を更新する
        Args:
            now_process_count (int): 全5工程
        !!注意!!
        必ずループ内で呼び出すこと。
        """
        self.window[self.PROG_BAR_KEY].update(now_process_count)
        
    
    
class LoadingAnimation(AbsGUIComponent):
    """_summary_\n
    ローディングアニメーションを表示するGUIコンポーネント。
    未実装。
    Args:
        AbsGUIComponent (_type_): _description
    """
    def __init__(self, msg:str, size:tuple[int, int], source_path:str) -> None:
        self.msg = msg
        self.width = size[0]
        self.height = size[1]
        self.source_path = source_path
        
    def _lay_out(self) -> list[list[any]]:
        
        L:list[list[any]] = [
            [gui.Text('ただいま処理中です。')],
            [gui.ProgressBar()] 
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