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
    
    @abstractmethod
    def _lay_out(self) -> list[list[any]]:
        """_summary_\n
        レイアウト配列を返す\n
        Returns:\n
            list[list]: GUIコンポーネントを格納した2次元配列\n
        """
        pass
    
    @abstractmethod
    def display(self) -> None:
        """_summary_\n
        ウィンドウを表示する
        """
        pass