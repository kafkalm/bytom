#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: gate.py
@time: 2019/5/13 013 12:23
@desc:
    https://www.gate.io/api2
    交易所行情 通过api抓取
    数据10秒更新一次 实时推送到前端展示
    BTM_USDT
'''
import scrapy
from bytom_crawler.items import GateDataItem

from db.MongoDB import MongoDBClient
from Log.logger import logger

import datetime
import time
import json
import hashlib

class GateSpider(scrapy.Spider):
    name = "gate"

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
        gate网站 10s更新一次数据 可以一直跑爬虫 间隔10s 获取最新数据
        :return:
        '''
        while True:
            yield scrapy.Request(
                url = 'https://data.gateio.co/api2/1/marketlist', # 交易市场详细行情
                callback = self.parse_marketlist,
                errback = self.err_parse,
                dont_filter = True
            )


    def parse_marketlist(self,response):
        try:
            ret = response.text
            js = json.loads(ret)
            data = js.get('data')
            btm_usdt = data[16]
            btm_btc = data[205]
            btm_eth = data[265]
            if btm_usdt.get('pair') != 'btm_usdt' or btm_btc.get('pair') != 'btm_btc' or btm_eth.get('pair') != 'btm_eth':
                for _ in data:
                    if _.get('pair') == 'btm_usdt':
                        btm_usdt = _
                    elif _.get('pair') == 'btm_btc':
                        btm_btc = _
                    elif _.get('pair') == 'btm_eth':
                        btm_eth = _

            btm_usdt_item = GateDataItem()
            btm_usdt_item['id'] = self._get_md5('btm_usdt'+ 'marketlist' + btm_usdt.get('rate'))
            btm_usdt_item['domain'] = 'gate'
            btm_usdt_item['param'] = 'marketlist-btm_usdt'
            btm_usdt_item['time'] = time.strftime('%Y-%m-%d %X', time.localtime())
            btm_usdt_item['data'] = btm_usdt

            btm_btc_item = GateDataItem()
            btm_btc_item['id'] = self._get_md5('btm_btc' + 'marketlist' + btm_btc.get('rate'))
            btm_btc_item['domain'] = 'gate'
            btm_btc_item['param'] = 'marketlist-btm_btc'
            btm_btc_item['time'] = btm_usdt_item['time']
            btm_btc_item['data'] = btm_btc

            btm_eth_item = GateDataItem()
            btm_eth_item['id'] = self._get_md5('btm_eth' + 'marketlist' + btm_eth.get('rate'))
            btm_eth_item['domain'] = 'gate'
            btm_eth_item['param'] = 'marketlist-btm_eth'
            btm_eth_item['time'] = btm_usdt_item['time']
            btm_eth_item['data'] = btm_eth

            yield btm_usdt_item
            yield btm_btc_item
            yield btm_eth_item

            yield scrapy.Request(
                url = 'https://data.gateio.co/api2/1/tickers',
                callback=self.parse_ticker,
                errback=self.err_parse,
                dont_filter=True
            )
        except Exception as e:
            logger.error("解析失败, error:%s" % str(e))
            return None

    def parse_ticker(self,response):
        try:
            ret = response.text
            js = json.loads(ret)
            btm_usdt = js.get('btm_usdt','')
            btm_btc = js.get('btm_btc','')
            btm_eth = js.get('btm_eth','')

            btm_usdt_item = GateDataItem()
            btm_usdt_item['id'] = self._get_md5('btm_usdt'+ 'ticker' + btm_usdt.get('quoteVolume'))
            btm_usdt_item['domain'] = 'gate'
            btm_usdt_item['param'] = 'ticker-btm_usdt'
            btm_usdt_item['time'] = time.strftime('%Y-%m-%d %X', time.localtime())
            btm_usdt_item['data'] = btm_usdt

            btm_btc_item = GateDataItem()
            btm_btc_item['id'] = self._get_md5('btm_btc' +'ticker' + btm_btc.get('quoteVolume'))
            btm_btc_item['domain'] = 'gate'
            btm_btc_item['param'] = 'ticker-btm_btc'
            btm_btc_item['time'] = btm_usdt_item['time']
            btm_btc_item['data'] = btm_btc

            btm_eth_item = GateDataItem()
            btm_eth_item['id'] = self._get_md5('btm_eth' + 'ticker' + btm_eth.get('quoteVolume'))
            btm_eth_item['domain'] = 'gate'
            btm_eth_item['param'] = 'ticker-btm_eth'
            btm_eth_item['time'] = btm_usdt_item['time']
            btm_eth_item['data'] = btm_eth

            yield btm_usdt_item
            yield btm_btc_item
            yield btm_eth_item

            yield scrapy.Request(
                url = 'https://data.gateio.co/api2/1/tradeHistory/btm_usdt',
                meta = {'key':'btm_usdt'},
                callback=self.parse_tradeHistory,
                errback=self.err_parse,
                dont_filter=True
            )

            yield scrapy.Request(
                url='https://data.gateio.co/api2/1/tradeHistory/btm_btc',
                meta={'key': 'btm_btc'},
                callback=self.parse_tradeHistory,
                errback=self.err_parse,
                dont_filter=True
            )

            yield scrapy.Request(
                url='https://data.gateio.co/api2/1/tradeHistory/btm_eth',
                meta={'key': 'btm_eth'},
                callback=self.parse_tradeHistory,
                errback=self.err_parse,
                dont_filter=True
            )
        except Exception as e:
            logger.error("解析失败, error:%s" % str(e))
            return None

    def parse_tradeHistory(self,response):
        try:
            ret = response.text
            js = json.loads(ret)
            if js.get('result') == "true":
                datas = js.get('data')
                for data in datas:
                    item = GateDataItem()
                    item['id'] = self._get_md5(data.get('tradeID'))
                    item['domain'] = 'gate'
                    item['param'] = 'tradeHistory-' + response.meta['key']
                    item['time'] = data.get('date','0000-00-00 00:00:00')
                    item['data'] = data
                    yield item
            time.sleep(3)
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