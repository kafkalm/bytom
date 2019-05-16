#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: coinmetrics.py
@time: 2019/4/22 022 11:38
@desc:
    coinmetrics.io 通过API抓取数据
    url : https://coinmetrics.io/api/v1/
    document : https://coinmetrics.io/api/
'''
import scrapy
from bytom_crawler.items import CoinmetricsSeedItem,CoinmetricsDataItem

from db.MongoDB import MongoDBClient
from Log.logger import logger

import datetime
import time
import json
import hashlib

class CoinmetricsSpider(scrapy.Spider):
    name = "coinmetrics"

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
            # 抓取时间段 时间戳格式
            start_time = datetime.datetime.strptime(self.settings.get('START_TIME'),'%Y-%m-%d')
            end_time = datetime.datetime.strptime(self.settings.get('END_TIME'),'%Y-%m-%d')
            while start_time <= end_time:
                body = {}
                body['url'] = 'https://coinmetrics.io/api/v1/'
                body['domain'] = 'coinmetrics'
                body['param'] = self.settings.get('CURRENCY_NAME')
                body['time'] = start_time.strftime('%Y-%m-%d')
                body['crawl_status'] = 0
                body['crawl_time'] = '0000-00-00'
                body['id'] = self._get_md5(body['url']+body['param']+body['time'])

                bodys.append(body)
                start_time += datetime.timedelta(days=1)

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
                "domain": "coinmetrics"
            }

            results = self.db.find(collection='seeds',query=query)
            items = []

            for result in results:
                item = CoinmetricsSeedItem()
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

                    # 基础 url 'https://coinmetrics.io/api/v1/'
                    # 获取所有支持的key

                    url = item.get('url') + 'get_available_data_types_for_asset/' + item.get('param')
                    yield scrapy.Request(
                        url = url,
                        meta = {'item':item},
                        callback = self.parse_key,
                        errback = self.err_parse,
                        dont_filter = True
                    )

    def parse_key(self,response):
        try:
            item = response.meta['item']
            ret = response.text
            js = json.loads(ret)
            keys = js.get('result',[])
            for key in keys:
                start_time = str(int(time.mktime(time.strptime(item.get('time'),'%Y-%m-%d'))))
                end_time = str(int(time.mktime(time.strptime(item.get('time'),'%Y-%m-%d')))+86400)
                url = item.get('url') + 'get_asset_data_for_time_range/' + item.get('param') + '/' \
                      + key + '/' + start_time + '/' + end_time
                yield scrapy.Request(
                    url = url,
                    meta = {'item':item,'key':key},
                    callback = self.parse_data,
                    errback = self.err_parse,
                    dont_filter = True
                )

        except Exception as e:
            logger.error("解析支持的Key失败, error:%s" % str(e))
            return None

    def parse_data(self,response):
        try:
            item = response.meta['item']
            key = response.meta['key']
            ret = response.text
            js = json.loads(ret)
            data = js.get('result',None)
            data_item = CoinmetricsDataItem()
            data_item['id'] = self._get_md5(item.get('param')+item.get('time')+key)
            data_item['domain'] = item.get('domain')
            data_item['name'] = item.get('param')
            data_item['data'] = {key:data}
            data_item['time'] = item.get('time')
            if not self.db.update_one(collection='seeds',query={'id':item.get('id')},body={'$set':{'crawl_status':1,'crawl_time':time.strftime('%Y-%m-%d %X', time.localtime())}}):
                logger.error("更新数据库seeds状态失败")
                return None
            return data_item

        except Exception as e:
            logger.error("解析data失败, error:%s" % str(e))
            return None

    def err_parse(self, failure):
        '''
        解析错误处理
        :param failure:
        :return:
        '''

        logger.error(repr(failure))

        yield failure.request





