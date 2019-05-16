# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BytomCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CoinmetricsSeedItem(scrapy.Item):

    id = scrapy.Field()     #id
    url = scrapy.Field()    #要爬取的url
    domain = scrapy.Field() #域名 后期用来筛选区分
    param = scrapy.Field()  #参数
    time = scrapy.Field()   #时间
    crawl_status = scrapy.Field()   #爬取状态
    crawl_time = scrapy.Field()   #爬取时间

class CoinmetricsDataItem(scrapy.Item):

    id = scrapy.Field()  # id
    domain = scrapy.Field() #域名
    name = scrapy.Field()  # 货币名称
    data = scrapy.Field()  # key-value对
    time = scrapy.Field()   #时间

class BlockMetaSeedItem(scrapy.Item):

    id = scrapy.Field()     #id
    url = scrapy.Field()    #要爬取的url
    domain = scrapy.Field() #域名 后期用来筛选区分
    page = scrapy.Field()  #页数
    crawl_status = scrapy.Field()   #爬取状态
    crawl_time = scrapy.Field()   #爬取时间

class BlockMetaDataItem(scrapy.Item):

    id = scrapy.Field()  # id
    domain = scrapy.Field() #域名
    timestamp = scrapy.Field()  #时间戳
    crawl_time = scrapy.Field() #抓取时间
    data = scrapy.Field()  # key-value对

class GateDataItem(scrapy.Item):

    id = scrapy.Field() # id
    domain = scrapy.Field() #域名
    param = scrapy.Field() #参数
    time = scrapy.Field()  #抓取时间
    data = scrapy.Field() # key-value对
