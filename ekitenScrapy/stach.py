    def __stop_spider(self):
        """
        [summary]\n 
        中断フラグがTrueになるか別スレッドで監視する。
        #このやり方は正直びみょい。
        """
        while True:
            if self.end_flg.value == True:
                self.middleware.stop()
                raise CloseSpider("spider cancelled")#無理やり例外をスローし終了。


    def start_requests(self):
        """
        Summary Lines
        店舗URLを取得する前処理。各ジャンルのページリンクを取得する。
        Yields:
            str: middlewareで返却された小ジャンルURL
        """
        visor = th.Thread(target=self.__stop_spider, daemon=True)
        visor.start()
        
        self.loading_flg.value = True
        
        for url in self.small_junle_url_list:
            yield scrapy.Request(url, callback=self.request_store_page, errback=self.error_process)
        
    def error_process(self, failure):#TODO:ステータスコードが400以上の場合は、リトライする。が、うまくいかない。
        """Summary Lines
        scrapy.Requestで例外発生時（response.stasusが400、500台）にcallbackする。\n
        後にリトライリクエストする。\n
        Args:
            failure (scrapy.Request): scrapy.Request
        """
        self.loading_flg.value = True
        print("####400 error catch####")
        time.sleep(500)#5分ほど待つ
        response = failure.value.response
        url = response.url
        if "shop_" in url:#shop_idが含まれているURLの場合。
            yield scrapy.Request(url, callback=self.parse, errback=self.error_process)
        else:
            yield scrapy.Request(url, callback=self.request_store_page, errback=self.error_process)
        #yield scrapy.Request(url, callback=self.request_store_page, errback=self.error_process)
        #self.RETRY_URL.append(url)
    
    def request_store_page(self, response):
        """Summary Lines
        店舗検索処理。スクレイピング処理をする店舗URLを取得する。
        Args:
            response (scrapy.Request): scrapy.Requestでyieldされたresonseオブジェクト

        Yields:
            scrapy.Request: スクレイピング先URL
        """
        #self.start_urls = self.search(response)
        self.loading_flg.value = True
        print(type(response.status))
        self.RETEYED = 0 #成功したらリトライカウントをリセット
        for elm in response.css('div.layout_media.p-shop_box_head > div.layout_media_wide > div > h2 > a'):
            href = elm.css('a::attr(href)').extract_first()
            url = response.urljoin(href)
            if url not in self.CRAWLED_URL:#重複スクレイピング対策
                self.CRAWLED_URL.append(url)
                yield scrapy.Request(url, callback=self.parse, errback=self.error_process)
                print("call store info scraping..")
        
        #次のページがあるかどうか
        next_page = response.css('div.p-pagination_next > a.button')
        print(next_page)
        if next_page.get() is not None:
            print("#####next page#####")
            next_page_url = response.urljoin(next_page.css('a::attr(href)').extract_first())
            print(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.request_store_page, errback=self.error_process)
