from __future__ import annotations
from abc import ABCMeta, abstractmethod

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
    
    def __init__(self)-> None:
        self.__event_handler:dict[str, dict[callable , tuple]] = {}
    
    @abstractmethod
    def _lay_out(self) -> list[list[any]]:
        """_summary_\n
        レイアウト配列を返す\n
        Returns:\n
            list[list]: GUIコンポーネントを格納した2次元配列\n
        """
        pass
    
    def addEventListener(self, key:str, callback:callable, *args) -> any:
        """_summary_\n
        イベントリスナーを設定する。\n
        Args:\n
            key: イベントキー\n
            callback: イベントハンドラー\n
            args: イベントハンドラーに渡す引数\n
        """
        self.__event_handler[key] = {callback : args}
        print(self.__event_handler)
    
    @abstractmethod
    def display(self) -> None:
        """_summary_\n
        ウィンドウを表示する.
        must use in while loop.
        """
        pass
    
    @abstractmethod
    def dispose(self) -> None:
        """_summary_\n
        ウィンドウを破棄する
        """
        pass