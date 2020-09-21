# -*- coding: utf-8 -*-
BOT_NAME = 'zp'

SPIDER_MODULES = ['zp.spiders']
NEWSPIDER_MODULE = 'zp.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'  #爬取的默认User-Agent，除非被覆盖。

# Obey robots.txt rules
ROBOTSTXT_OBEY =False

ITEM_PIPELINES = {
   'zp.pipelines.DataCleanPipeline': 100,
   'zp.pipelines.DataTimePipeline': 200,
   'zp.pipelines.DuplicatesPipeline': 50,
   'zp.pipelines.MysqlSavePipeline': 300,
}
# LOG_FILE='zhaopin.log' #logging输出的文件名
# LOG_LEVEL='ERROR'       #log的最低级别。
# LOG_STDOUT=True        #进程所有的标准输出(及错误)将会被重定向到log中。
CONCURRENT_ITEMS=200 #Item Processor(即 Item Pipeline) 同时处理(每个response的)item的最大值。
CONCURRENT_REQUESTS=20 #Scrapy downloader 并发请求(concurrent requests)的最大值。
CONCURRENT_REQUESTS_PER_DOMAIN=10 #对单个网站进行并发请求的最大值。
DEFAULT_REQUEST_HEADERS={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}  #默认headers

# 自定义Mysql链接参数
MYSQL_HOST = 'fan'
MYSQL_USER='root'
MYSQL_PASSWD='FanTan879'
MYSQL_DB='zp'