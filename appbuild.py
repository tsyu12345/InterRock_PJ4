from __future__ import annotations
from typing import Final as const
import subprocess


class BuildParamInterface():
    """_summary_\n
    ビルドに使用するパラメーター
    """
    
    def __init__(self, target:str, icon: str|None = None, binarys: list[str]|None = None, compile_one_file:bool|None=False, hidden_import:list[str]|None=None) -> None:
        self.TARGET_FILE:str = target
        self.ICON_PATH:str|None = icon
        self.BINARYS:list[str]|None = binarys
        self.DO_ONEFILE:bool|None = compile_one_file
        self.HIDDEN_IMPORTS:list[str]|None = hidden_import
        


class AppBuild():
    """_summary_\n
    コマンドを実行しアプリケーションのビルドを行う
    """
    
    BUILDER: const[str] = "pyinstaller"
    BUILDABLE: const[list[str]] = [
        ".py"
        ".spec"
    ]
    
    def __init__(self, param:BuildParamInterface) -> None:
        self.param = param
        self.output = self.__get_output_dir()
        
    def __binary_build(self) -> None:
        """_summary_\n
        .py -> .exeの変換を行う。
        """
        command:str = self.BUILDER + " " + self.param.TARGET_FILE
        if self.param.ICON_PATH is not None:
            command += " --icon=" + self.param.ICON_PATH
        if self.param.DO_ONEFILE is True:
            command += " --onefile"
            
        if self.param.HIDDEN_IMPORTS is not None:
            for module in self.param.HIDDEN_IMPORTS:
                command += " --hidden-import " + module + " "
        
        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as err:
            print(err)
            
    
    def __copy_binary(self, binary:str, target:str) -> None:
        """_summary_\n
        バイナリファイルをdistにコピーする
        """
        command:const[str] = "cp -r -v " + binary + " " + target

        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as err:
            print(err)
    
    
    def build(self):
        """_summary_\n
        ビルドを実行する。
        """
        self.__binary_build()
        
        if self.param.BINARYS is not None:
            for path in self.param.BINARYS:
                self.__copy_binary(path, self.output)
        if self.param.ICON_PATH is not None:
            self.__copy_binary(self.param.ICON_PATH, self.output)
            
        print("Build Complete!")
        print("Output: " + self.output)
        
    
    
    def __get_output_dir(self) -> str:
        """_summary_\n
        ファイル名を取得する（拡張子の除く純粋なファイル名文字列）
        ※Pyinstallerはファイル名フォルダ直下にexeを生成するため。
        """
        filename:str = self.param.TARGET_FILE.split("/")[-1].replace(".py", "")
        return "dist/" + filename
    
if __name__ == "__main__":
    
    buildParam = BuildParamInterface(
        "ekitenScrapy/main.py",
        icon="1258d548c5548ade5fb2061f64686e40_xxo.ico",
        binarys=["bin"],
        compile_one_file=False,
        hidden_import=[
            'scrapy.spiderloader', 
            'scrapy.statscollectors', 
            'scrapy.logformatter', 
            'scrapy.extensions', 
            'scrapy.extensions.corestats', 
            'scrapy.extensions.corestats', 
            'scrapy.extensions.telnet', 
            'scrapy.extensions.memusage', 
            'scrapy.extensions.memdebug', 
            'scrapy.extensions.closespider', 
            'scrapy.extensions.feedexport', 
            'scrapy.extensions.logstats', 
            'scrapy.extensions.spiderstate', 
            'scrapy.extensions.throttle', 
            'scrapy.core.scheduler', 
            'scrapy.squeues', 
            'queuelib', 
            'scrapy.core.downloader', 
            'scrapy.downloadermiddlewares', 
            'scrapy.downloadermiddlewares.robotstxt', 
            'scrapy.downloadermiddlewares.httpauth', 
            'scrapy.downloadermiddlewares.downloadtimeout', 
            'scrapy.downloadermiddlewares.defaultheaders', 
            'scrapy.downloadermiddlewares.useragent', 
            'scrapy.downloadermiddlewares.retry', 
            'scrapy.downloadermiddlewares.ajaxcrawl', 
            'scrapy.downloadermiddlewares.redirect', 
            'scrapy.downloadermiddlewares.httpcompression', 
            'scrapy.downloadermiddlewares.redirect', 
            'scrapy.downloadermiddlewares.cookies', 
            'scrapy.downloadermiddlewares.httpproxy', 
            'scrapy.downloadermiddlewares.stats', 
            'scrapy.downloadermiddlewares.httpcache', 
            'scrapy.spidermiddlewares', 
            'scrapy.spidermiddlewares.httperror', 
            'scrapy.spidermiddlewares.offsite', 
            'scrapy.spidermiddlewares.referer', 
            'scrapy.spidermiddlewares.urllength', 
            'scrapy.spidermiddlewares.depth', 
            'scrapy.pipelines', 
            'scrapy.dupefilters', 
            'scrapy.core.downloader.handlers.datauri', 
            'scrapy.core.downloader.handlers.file', 
            'scrapy.core.downloader.handlers.http', 
            'scrapy.core.downloader.handlers.s3', 
            'scrapy.core.downloader.handlers.ftp', 
            'scrapy.core.downloader.webclient', 
            'scrapy.core.downloader.contextfactory', 
            'scrapy_xlsx',
            'ekitenScrapy.settings', 
            'ekitenScrapy.spiders',
            'chromedriver_binary'
        ]
    )
    
    AppBuild(buildParam).build()