# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from db.MongoDB import MongoDBClient
from mykafka.kafka_client import MyKafkaProducer
from bytom_crawler.items import CoinmetricsDataItem,BlockMetaDataItem,GateDataItem
import json

class BytomCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class KafkaPipeline(object):
    '''
    推送数据到kafka的pipeline
    数据清洗交由spark-streaming处理
    '''

    def __init__(self,settings):

        self.settings = settings
        # kafka producer实例化
        self.producer = MyKafkaProducer(self.settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def process_item(self, item, spider):
        '''
        推送数据到broker
        :param item:
        :param spider:
        :return:
        '''
        if isinstance(item,CoinmetricsDataItem):
            data = dict(item)
            data = json.dumps(data,ensure_ascii=False).encode('utf-8')
            self.producer.sendMsg(topic='coinmetrics_data',msg=data)
            return item

        elif isinstance(item,BlockMetaDataItem):
            data = dict(item)
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.producer.sendMsg(topic='blockmeta_data', msg=data)
            return item

        elif isinstance(item,GateDataItem):
            data = dict(item)
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.producer.sendMsg(topic='gate_data', msg=data)
            return item

    def close_spider(self,spider):
        '''
        爬虫结束时 处理所有未同步的消息 断开kafka生产者连接
        :param spider:
        :return:
        '''
        self.producer.flushMsg()
        self.producer._close_producer()

class MongoDBPipeline(object):
    '''
    存储数据到MongoDB的pipeline
    '''

    def __init__(self,settings):

        self.settings = settings
        # 数据库实例化
        self.db = MongoDBClient(self.settings)
        # 缓存区
        self.cache = []

    @classmethod
    def from_crawler(cls,crawler):
        return cls(settings=crawler.settings)

    def process_item(self, item, spider):
        '''
        处理item 批量存储到MongoDB
        :param item:
        :param spider:
        :return:
        '''
        if isinstance(item,CoinmetricsDataItem):
            self.cache.append(dict(item))
            if len(self.cache) == 1000:
                self.db.insert_many('coinmetrics_data',self.cache)
                # 清空缓存区
                self.cache.clear()
            return item

        # 存量数据管道
        # elif isinstance(item,BlockMetaDataItem):
        #     self.cache.append(dict(item))
        #     if len(self.cache) == 1000:
        #         self.db.insert_many('blockmeta_data', self.cache)
        #         # 清空缓存区
        #         self.cache.clear()
        #     return item

        # 实时数据去重管道
        elif isinstance(item,BlockMetaDataItem):
            for _ in self.cache:
                if _['id'] == item['id']:
                    return None
            if not self.db.find(collection='blockmeta_data',query={'id':item['id']}):
                self.cache.append(dict(item))
            if len(self.cache) == 10:
                self.db.insert_many('blockmeta_data', self.cache)
                # 清空缓存区
                self.cache.clear()
            return item

        elif isinstance(item,GateDataItem):
            for _ in self.cache:
                if _['id'] == item['id']:
                    return None
            if not self.db.find(collection='gate_data',query={'id':item['id']}):
                self.cache.append(dict(item))
            if len(self.cache) == 1:
                self.db.insert_many('gate_data', self.cache)
                # 清空缓存区
                self.cache.clear()
            return item

    def close_spider(self,spider):
        '''
        爬虫结束时 把缓存区存入数据库 断开数据库连接
        :param spider:
        :return:
        '''
        if self.cache:
            if self.cache[0].get('domain',None) == 'coinmetrics':
                self.db.insert_many('coinmetrics_data',self.cache)
            elif self.cache[0].get('domain',None) == 'blockmeta':
                self.db.insert_many('blockmeta_data',self.cache)
            elif self.cache[0].get('domain',None) == 'gate':
                self.db.insert_many('gate_data',self.cache)
        self.db._close()