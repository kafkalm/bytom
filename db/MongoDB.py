#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: MongoDB.py
@time: 2019/4/22 022 14:43
@desc:
    MongoDB 数据库操作封装
'''

import pymongo
from Log.logger import logger

class MongoDBClient():
    def __init__(self,settings):
        '''
        settings = {
            'MONGODB_URL': str, #MONGODB的URL地址
            'MONGODB_DB': str,  #数据库名
            'MONGODB_BATCH_SIZE' : INT #读取数量
        }
        :param settings:
        '''
        self.settings = settings
        self.MONGODB_URL = self.settings.get('MONGODB_URL',None)
        self.client = None
        self.db = None
        self.batch_size = self.settings.get('MONGODB_BATCH_SIZE',0)

        self._get_db()

    def _connect(self):
        '''
        与MongoDB客户端建立连接
        :return:
        '''
        try:
            self.client = pymongo.MongoClient(self.MONGODB_URL)
            return True
        except Exception as e:
            logger.error("连接MongoDB失败, error:%s" % str(e))
            return False

    def _close(self):
        '''
        与MongoDB客户端断开连接
        可以手动关闭连接 释放资源
        也可以等待python自动垃圾回收
        :return:
        '''
        try:
            if self.client:
                self.client.close()
                return True
            return False
        except Exception as e:
            logger.error("关闭MongoDB失败, error:%s" % str(e))
            return False

    def _get_db(self):
        '''
        选择一个MongoDB数据库
        如果连接失败 返回False
        连接成功 返回True
        :return:
        '''
        try:
            if self._connect():
                if self.settings.get('MONGODB_DB',None) in self.client.list_database_names():
                    self.db = self.client[self.settings.get('MONGODB_DB',None)]
                    return True
                else:
                    logger.warning("不存在名为 %s 的MongoDB数据库" % str(self.settings.get('MONGODB_DB',None)))
                    return False
            return False
        except Exception as e:
            logger.error("获取MongoDB数据库失败, error:%s" % str(e))
            return False

    def _get_collection(self,collection:str):
        '''
        获取MongoDB数据库中的一个集合
        :param collection:
        :return:
            MongoDB数据库集合实例
            不存在返回None
        '''

        try:
            if self.db:
                if collection in self.db.list_collection_names():
                    return self.db[collection]
                else:
                    return None
            else:
                logger.warning("没有选择MongoDB数据库")
                return None
        except Exception as e:
            logger.error("获取MongoDB集合失败, error:%s" % str(e))
            return None

    def insert_one(self,collection:str,body:dict):
        '''
        插入操作
        :return: True or False
        '''
        try:
            # 获取集合
            col = self._get_collection(collection)
            col.insert_one(body)

            return True
        except Exception as e:
            logger.error("插入信息失败, error:%s" % str(e))
            return False

    def insert_many(self,collection:str,body:list):
        '''
        批量插入
        body [ {}, {}, {},...]
        :param collection: 集合名
        :param body: 插入的内容
        :return:
        '''
        try:
            col = self._get_collection(collection)
            col.insert_many(body)

            return True
        except Exception as e:
            logger.error("批量插入信息失败, error:%s" % str(e))
            return False

    def find(self,collection:str,query:dict):
        '''
        查询
        :param collection: 集合名
        :param query: 查询条件
        :return: 查询结果 List
        '''
        try:
            col = self._get_collection(collection)

            results = col.find(query).batch_size(self.batch_size)

            result_list = list(results)

            return result_list
        except Exception as e:
            logger.error("查询信息失败, error:%s" % str(e))
            return None

    def find_sort_limit(self,collection:str,query:dict,sort:dict,limit:int,get_data:bool=False):
        '''
        排序限数差
        :param collection: 集合名
        :param query: 查询条件
        :param sort: 排序条件
        :param limit: 限制数量
        :param get_data: 是否直接返回数据库中的data字段 默认 False
        :return: 查询结果 List
        '''
        try:
            col = self._get_collection(collection)
            (field,flag), = sort.items()
            if flag == 1:
                flag = pymongo.ASCENDING
            else:
                flag = pymongo.DESCENDING

            result_list = []
            results = col.find(query).sort(field,flag).limit(limit)

            if get_data:
                for result in results:
                    if result.get('data',None):
                        result_list.append(result.get('data'))
            else:
                result_list = list(results)

            return result_list
        except Exception as e:
            logger.error("查询信息失败, error:%s" % str(e))
            return None

    def update_one(self,collection:str,query:dict,body:dict):
        '''
        单条更新
        建议用 id 作为查询条件
        通过 from bson.objectid import ObjectId 可以用 '_id" 进行查询
        :param collection: 集合名
        :param query: 查询条件
        :param body: 更新的内容
        :return: True or False
        '''
        try:
            col = self._get_collection(collection)

            #先查询 再更新
            results = self.find(collection = collection,query=query)
            if not results or len(results) == 0:
                logger.warning("不存在该文档")
                return False

            col.update_one(query,body)

            return True
        except Exception as e:
            logger.error("更新信息失败, error:%s" % str(e))
            return False

    def update_many(self,collection:str,query:dict,body:list):
        '''
        批量更新
        :param collection: 集合名
        :param query: 查询条件
        :param body: 更新的内容
        :return: True or False
        '''
        try:
            col = self._get_collection(collection)

            # 先查询 再更新
            results = self.find(collection=collection, query=query)
            if not results or len(results) == 0:
                logger.warning("不存在该文档")
                return False

            col.update_many(query,body)

            return True
        except Exception as e:
            logger.error("批量更新信息失败, error:%s" % str(e))
            return False

    def delete_one(self,collection:str,query:dict):
        '''
        单条删除
        :param collection: 集合名
        :param query: 查询条件
        :return: True or False
        '''
        try:
            col = self._get_collection(collection)

            # 先查询 再删除
            results = self.find(collection=collection, query=query)
            if not results or len(results) == 0:
                logger.warning("不存在该文档")
                return False

            col.delete_one(query)

            return True
        except Exception as e:
            logger.error("删除信息失败, error:%s" % str(e))
            return False

    def delete_many(self, collection: str, query: dict):
        '''
        批量删除
        :param collection: 集合名
        :param query: 查询条件
        :return: True or False
        '''
        try:
            col = self._get_collection(collection)

            # 先查询 再删除
            results = self.find(collection=collection, query=query)
            if not results or len(results) == 0:
                logger.warning("不存在该文档")
                return False

            result = col.delete_many(query)
            logger.info("共删除了 %d 个文档" % result.deleted_count)

            return True
        except Exception as e:
            logger.error("批量删除信息失败, error:%s" % str(e))
            return False

