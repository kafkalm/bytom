#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: blockmeta_update.py
@time: 2019/5/16 016 17:07
@desc:
    blockmeta数据实时更新
'''
#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: blockmeta.py
@time: 2019/5/13 013 10:37
@desc:
    https://blockmeta.com/api/v2
    通过api抓取
'''

import scrapy
from bytom_crawler.items import BlockMetaSeedItem,BlockMetaDataItem

from db.MongoDB import MongoDBClient
from Log.logger import logger

import time
import json
import hashlib

class BlockMetaSpider(scrapy.Spider):
    name = "blockmeta_update"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''
        创建spider 初始化一些参数
        :param crawler:
        :param args:
        :param kwargs:
        :return:
        '''

        s = cls(*args, **kwargs)
        s._set_crawler(crawler)
        s._initial()

        return s

    def _initial(self):
        '''
        初始化 spider
        :return:
        '''

        #数据库实例化
        self.db = MongoDBClient(self.settings)

        #加载任务的标识 置为True会一直加载任务
        self.load_flag = True

        #生成任务标识
        self.gen_flag = self.settings.get('GEN_SEEDS_FLAG')

    def _get_md5(self,s):
        try:
            if not s:
                s = ''
            return hashlib.md5(str(s).encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error("Generate md5 failed ,error:%s" % str(e))
            return None

    def start_requests(self):
        '''
        重写start_requests方法 动态加载
        :return:
        '''
        while True:
            time.sleep(5)
            # 循环抓取最新的交易信息
            url = 'https://blockmeta.com/api/v2/transactions?page=1&limit=10'
            yield scrapy.Request(
                url = url,
                callback = self.parse_transactions,
                errback = self.err_parse,
                dont_filter = True
            )

    def parse_transactions(self,response):
        try:
            ret = response.text
            js = json.loads(ret)
            for transaction in js.get('transactions'):
                transaction_item = BlockMetaDataItem()
                transaction_item['id'] = transaction.get('id')
                transaction_item['domain'] = 'blockmeta'
                transaction_item['timestamp'] = transaction.get('timestamp')
                transaction_item['crawl_time'] = time.strftime('%Y-%m-%d %X', time.localtime())
                transaction_item['data'] = transaction

                yield transaction_item

        except Exception as e:
            logger.error("解析失败, error:%s" % str(e))
            return None

    def err_parse(self, failure):
        '''
        解析错误处理
        :param failure:
        :return:
        '''

        logger.error(repr(failure))

        yield failure.request