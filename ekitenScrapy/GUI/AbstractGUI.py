from __future__ import annotations
from typing import Any, Final as const, Callable
from abc import ABCMeta, abstractmethod
from PySimpleGUI.PySimpleGUI import Window

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

class AbsWindowComponent(object, metaclass=ABCMeta):
    """[summary]\n
    windowレベルの基底抽象クラス定義。
    """
    
    def __init__(self, window_name=None)-> None:
        self.event_handler:dict[str, list[Callable | tuple]] = {} #TODO:EventHandlerオブジェクトの定義をつくり、それで注釈する。
        self.event:str = ""
        self.value:dict[str, str] = {}
        self.window:Window = Window(window_name)
    
    @abstractmethod
    def _lay_out(self) -> list[list[Any]]:
        """_summary_\n
        レイアウト配列を返す\n
        Returns:\n
            list[list]: GUIコンポーネントを格納した2次元配列\n
        """
        pass
    
    def addEventListener(self, key:str, callback:Callable, *args) -> None:
        """_summary_\n
        イベントリスナーを設定する。\n
        Args:\n
            key: イベントキー\n
            callback: イベントハンドラー\n
            args: イベントハンドラーに渡す引数\n
        """
        self.event_handler[key] = [callback, args]
        print(self.event_handler)
        
    def __catchEvent(self) -> None:
        """_summary_\n
        イベントをキャッチする。\n
        """
        if self.event in self.event_handler:
            
            callback:Callable = self.event_handler[self.event][0]
            args:tuple = self.event_handler[self.event][1]
            
            if args == ():
                callback()
            else:
                callback(args)
    
    def display(self) -> None:
        """_summary_\n
        ウィンドウを表示する.
        must use in while loop.
        """
        self.event, self.value = self.window.read()
        self.__catchEvent()
    
    @abstractmethod
    def dispose(self) -> None:
        """_summary_\n
        ウィンドウを破棄する
        """
        pass