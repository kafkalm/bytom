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
    name = "blockmeta"

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

    def _gen_seeds(self):
        '''
        根据 settings 中的时间设置 , 自动生成任务
        :return:
        '''
        try:
            bodys = []
            body = {}
            body['url'] = 'https://blockmeta.com/api/v2/'
            body['domain'] = 'blockmeta'
            body['crawl_status'] = 0
            body['crawl_time'] = '0000-00-00'
            body['page'] = 1
            body['id'] = self._get_md5(body['url'])
            bodys.append(body)

            if not self.db.insert_many(collection='seeds',body=bodys):
                logger.error("生成数据库seeds失败")
                return None

        except Exception as e:
            logger.error("生成数据库seeds失败, error:%s" % str(e))
            return None

    def _load_seeds(self):
        '''
        从数据库中加载任务 并转换为item
        :return: list[item] or None
        '''
        try:
            #生成种子
            if self.gen_flag:
                self._gen_seeds()

            query = {
                "crawl_status" : 0,
                "domain": "blockmeta"
            }

            results = self.db.find(collection='seeds',query=query)
            items = []

            for result in results:
                item = BlockMetaSeedItem()
                for key in result.keys():
                    if key == '_id':
                        continue
                    else:
                        item[key] = result.get(key)

                item['crawl_status'] = 2

                if not self.db.update_one(collection='seeds',query={'id':item.get('id')},body={'$set':{'crawl_status':item['crawl_status']}}):
                    logger.error("更新数据库seeds状态失败,返回部分seeds")
                    return items

                items.append(item)

            return items

        except Exception as e:
            logger.error("读取数据库seeds失败, error:%s" % str(e))
            return None

    def start_requests(self):
        '''
        重写start_requests方法 动态加载
        :return:
        '''
        while self.load_flag:
            items = self._load_seeds()
            self.gen_flag = False

            if not items:
                self.load_flag = False
            else:
                for item in items:

                    # 基础 url 'https://blockmeta.com/api/v2/'
                    # 获取所有支持的key

                    url = item.get('url') + 'transactions?page={page}&limit=100'.format(page=item.get('page'))
                    yield scrapy.Request(
                        url = url,
                        meta = {'item':item},
                        callback = self.parse_transactions,
                        errback = self.err_parse,
                        dont_filter = True
                    )

    def parse_transactions(self,response):
        try:
            item = response.meta['item']
            ret = response.text
            js = json.loads(ret)
            page = js.get('pagination').get('current') + 1
            for transaction in js.get('transactions'):
                transaction_item = BlockMetaDataItem()
                transaction_item['id'] = transaction.get('id')
                transaction_item['domain'] = item.get('domain')
                transaction_item['timestamp'] = transaction.get('timestamp')
                transaction_item['crawl_time'] = time.strftime('%Y-%m-%d %X', time.localtime())
                transaction_item['data'] = transaction

                yield transaction_item

            if not self.db.update_one(collection='seeds',query={'id':item.get('id')},body={'$set':{'page':page,'crawl_time':time.strftime('%Y-%m-%d %X', time.localtime())}}):
                logger.error("更新数据库seeds状态失败")
                return None

            url = item.get('url') + 'transactions?page={page}&limit=100'.format(page=page)

            if page * 100 <= js.get('pagination').get('total'):
                yield scrapy.Request(
                    url = url,
                    meta = {'item':item},
                    callback = self.parse_transactions,
                    errback = self.err_parse,
                    dont_filter = True
                )
            else:
                if not self.db.update_one(collection='seeds', query={'id': item.get('id')},
                                          body={'$set': {'crawl_status': 1}}):
                    logger.error("更新数据库seeds状态失败")
                    return None

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


