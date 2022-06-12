# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['ekitenScrapy\\main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=['scrapy.spiderloader', 'scrapy.statscollectors', 'scrapy.logformatter', 'scrapy.extensions', 'scrapy.extensions.corestats', 'scrapy.extensions.corestats', 'scrapy.extensions.telnet', 'scrapy.extensions.memusage', 'scrapy.extensions.memdebug', 'scrapy.extensions.closespider', 'scrapy.extensions.feedexport', 'scrapy.extensions.logstats', 'scrapy.extensions.spiderstate', 'scrapy.extensions.throttle', 'scrapy.core.scheduler', 'scrapy.squeues', 'queuelib', 'scrapy.core.downloader', 'scrapy.downloadermiddlewares', 'scrapy.downloadermiddlewares.robotstxt', 'scrapy.downloadermiddlewares.httpauth', 'scrapy.downloadermiddlewares.downloadtimeout', 'scrapy.downloadermiddlewares.defaultheaders', 'scrapy.downloadermiddlewares.useragent', 'scrapy.downloadermiddlewares.retry', 'scrapy.downloadermiddlewares.ajaxcrawl', 'scrapy.downloadermiddlewares.redirect', 'scrapy.downloadermiddlewares.httpcompression', 'scrapy.downloadermiddlewares.redirect', 'scrapy.downloadermiddlewares.cookies', 'scrapy.downloadermiddlewares.httpproxy', 'scrapy.downloadermiddlewares.stats', 'scrapy.downloadermiddlewares.httpcache', 'scrapy.spidermiddlewares', 'scrapy.spidermiddlewares.httperror', 'scrapy.spidermiddlewares.offsite', 'scrapy.spidermiddlewares.referer', 'scrapy.spidermiddlewares.urllength', 'scrapy.spidermiddlewares.depth', 'scrapy.pipelines', 'scrapy.dupefilters', 'scrapy.core.downloader.handlers.datauri', 'scrapy.core.downloader.handlers.file', 'scrapy.core.downloader.handlers.http', 'scrapy.core.downloader.handlers.s3', 'scrapy.core.downloader.handlers.ftp', 'scrapy.core.downloader.webclient', 'scrapy.core.downloader.contextfactory', 'scrapy_xlsx', 'ekitenScrapy.settings', 'ekitenScrapy.spiders', 'chromedriver_binary'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='1258d548c5548ade5fb2061f64686e40_xxo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
