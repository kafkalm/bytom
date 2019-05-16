#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: spark_streaming.py
@time: 2019/4/23 023 16:57
@desc:
    spark streaming 封装
    消费kafka推送的消息
    spark 2.3.0 以上版本已被弃用
'''

from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils,TopicAndPartition
import json
from db.MongoDB import MongoDBClient
from Log.logger import logger

class SparkStreaming():
    def __init__(self,spark_settings,mongodb_settings):
        '''
        spark_settings = {
            'spark_cores_max' : int , # 运行Spark核心最大数量
            'appName' : str , # 名称
            'batchDuration' : int , # Spark Streaming批次间隔
            'brokers' : str , # kafka brokers ip地址 "host:port,host:port,..."
            'topics' : list , # kafka topic [ topic(str) ]
        }
        mongodb_settings = {
            'MONGODB_URL': str, #MONGODB的URL地址
            'MONGODB_DB': str,  #数据库名
            'MONGODB_BATCH_SIZE' : INT #读取数量
        }
        :param spark_settings:
        :param mongodb_settings:
        '''
        self.spark_settings = spark_settings
        self.mongodb_settings = mongodb_settings
        self.sconf = SparkConf()
        self.sconf.set('spark.cores.max',self.spark_settings.get('spark_cores_max',4))
        self.sc = SparkContext(appName=self.spark_settings.get('appName','NoName'),conf=self.sconf)
        self.ssc = StreamingContext(self.sc,batchDuration=self.spark_settings.get('batchDuration',10))
        self.brokers = self.spark_settings.get('brokers',None)
        self.kafkaStreams = KafkaUtils.createDirectStream(ssc = self.ssc,topics=self.spark_settings.get('topics',None),
                                                          kafkaParams={"metadata.broker.list": self.brokers},
                                                          fromOffsets={TopicAndPartition(self.spark_settings.get('topics',None)[0], 0): 0})
        self.offsetRanges = []
        self.db = MongoDBClient(self.mongodb_settings)

    def _start(self):
        self.ssc.start()
        self.ssc.awaitTermination()

    def _stop(self):
        self.ssc.stop()

    def _offset(self,rdd):
        '''
        存储offset信息
        :param rdd:
        :return:
        '''
        self.offsetRanges = rdd.offsetRanges()

    def data_clean(self):
        def json_deal(rdd):
            try:
                js = json.loads(rdd[1],encoding='utf-8')
                if js.get('domain','') == 'coinmetrics':
                    # 所需字段
                    need_fields = ['price(usd)', 'txvolume(usd)', 'exchangevolume(usd)', 'mediantxvalue(usd)']
                    data = js.get('data',None)
                    if data:
                        for key in data.keys():
                            if key in need_fields:
                                if data[key]:
                                    for _ in data[key]:
                                        return {'name':js.get('name'),'domain':js.get('domain'),'data':js.get('data'),
                                                'time':js.get('time')}
                                else:
                                    return None
                            else:
                                return None
                elif js.get('domain','') == 'blockmeta':
                    # 所需字段
                    need_fields = ['transaction_amount']
                    data = js.get('data', None)
                    return {'name':'btm','domain':js.get('domain'),'transaction_amount':data.get('transaction_amount',None),'time':data.get('timestamp',None)}
            except Exception:
                return None

        def store(rdd):
            try:
                data = rdd[0]
                if data.get('domain') == 'coinmetrics':
                    if not self.db.insert_one(collection='coinmetrics_deal_data',body=data):
                        logger.error("存储到coinmetrics_deal_data失败")
                        return None
                elif data.get('domain') == 'blockmeta':
                    if not self.db.insert_one(collection='blockmeta_deal_data',body=data):
                        logger.error("存储到blockmeta_deal_data失败")
                        return None

            except Exception:
                return None
        #清洗数据
        data = self.kafkaStreams.map(json_deal)
        #存储清洗的数据
        data.foreachRDD(lambda rdd:rdd.foreach(store))
        #更新offset
        data.foreachRDD(self._offset)

        self._start()
