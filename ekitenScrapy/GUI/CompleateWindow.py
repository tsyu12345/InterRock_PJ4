from __future__ import annotations
from AbstractGUI import *
import PySimpleGUI as gui

class CompleateWindow(AbsWindowComponent):
    
    def __init__(self,title:str):
        super().__init__(title)
        
    def _lay_out(self) -> list[list[any]]:
        L:list[list] = [
            [],
            [],
        ]
        
        return L
    
    def dispose(self) -> None:
        self.window.close()
