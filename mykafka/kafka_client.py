#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: mykafka.py
@time: 2019/4/23 023 14:41
@desc:
    mykafka-python 封装
'''
from kafka import KafkaProducer
from kafka.errors import KafkaError

import hashlib
import time
from Log.logger import logger


class MyKafkaProducer():
    def __init__(self,settings):
        '''
        settings = {
            'client_id': str,
            'bootstrap_servers': 'host[:port]' or list of 'host[:port]',
            'batch_size': int,
            'value_serializer': callable
        }
        :param settings:
        '''
        self.settings = settings.get('KAFKA_CONF')
        self.bootstrap_servers = self.settings.get('bootstrap_servers',None)
        self.client_id = self.settings.get('client_id',self._get_md5(time.time()))
        self.batch_size = self.settings.get('batch_size',10000)
        self.value_serializer = self.settings.get('value_serializer',None)
        self.producer = self._get_producer()

    def _get_producer(self):
        '''
        实例化生产者
        :return:
        '''
        try:
            producer = KafkaProducer(bootstrap_servers = self.bootstrap_servers,
                                          client_id = self.client_id,
                                          batch_size = self.batch_size,
                                          value_serializer = self.value_serializer)
            return producer
        except Exception as e:
            logger.error("Get consumer id:%s failed ,error:%s" % (str(self.client_id),str(e)))
            return None

    def _close_producer(self):
        '''
        结束生产者实例
        :return:
        '''
        try:
            if self.producer:
                self.producer.close()
                return True
            return False
        except Exception as e:
            logger.error("Close consumer id:%s failed ,error:%s" % (str(self.client_id), str(e)))
            return False

    def _get_md5(self,s):
        try:
            if not s:
                s = ''
            return hashlib.md5(str(s).encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error("Generate md5 failed ,error:%s" % str(e))
            return None

    def _on_send_success(self,record_metadata):

        logger.info('Topic: %s Partition: %d Offset: %s' % (record_metadata.topic,record_metadata.partition,record_metadata.offset))

    def _on_send_error(self,excp):

        logger.error(str(excp))

    def sendMsg(self,topic,msg):
        '''
        推送消息
        :param msg: byte
        :param topic: str
        :return:
        '''
        try:
            if not self.producer:
                self._get_producer()
            self.producer.send(topic,value=msg,key=self.client_id.encode('utf-8')).add_callback(self._on_send_success).add_errback(self._on_send_error)

        except Exception as e:
            logger.error("Send message failed ,error:%s" % str(e))
            return None

    def flushMsg(self):
        '''
        确保消息
        :return:
        '''
        try:
            if not self.producer:
                self._get_producer()
            self.producer.flush()

        except Exception as e:
            logger.error("Flush message failed ,error:%s" % str(e))
            return None
