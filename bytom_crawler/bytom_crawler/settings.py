# -*- coding: utf-8 -*-

# Scrapy settings for bytom_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'bytom_crawler'

SPIDER_MODULES = ['bytom_crawler.spiders']
NEWSPIDER_MODULE = 'bytom_crawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'bytom_crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'bytom_crawler.middlewares.BytomCrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'bytom_crawler.middlewares.BytomCrawlerDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'bytom_crawler.pipelines.BytomCrawlerPipeline': None,
    'bytom_crawler.pipelines.KafkaPipeline': None,
    'bytom_crawler.pipelines.MongoDBPipeline': 1,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# redis连接
REDIS_URL = 'redis://127.0.0.1:6379/0'

# 在关闭时候保留原来的调度器和去重记录
SCHEDULER_PERSIST = True

# 在开始之前清空调度器和去重记录
SCHEDULER_FLUSH_ON_START = True

# 优先级queue
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
# 调度队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 去重规则
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# Number of Hash Functions to use, defaults to 6
BLOOMFILTER_HASH_NUMBER = 6

# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
# 布隆过滤器在redis中的内存位，在拥有最优值且误判率在1%的布隆过滤器中， 2^22 = 4Mb,约可以去重40w数据
BLOOMFILTER_BIT = 22


# MONGODB 相关配置
MONGODB_URL = 'mongodb://localhost:27017/'
MONGODB_DB = 'bytom'
MONGODB_BATCH_SIZE = 100

# kafka 相关配置
KAFKA_CONF = {
    'bootstrap_servers':['127.0.0.1:9092'],
    'batch_size':100
}

# 抓取日期配置
START_TIME = '2019-05-13'
END_TIME = '2019-05-15'

# 是否生成任务
GEN_SEEDS_FLAG = True

# 货币名称
CURRENCY_NAME = 'btm'