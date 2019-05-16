#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: test.py
@time: 2019/5/15 015 20:34
@desc:
'''
from db.MongoDB import MongoDBClient
from config.config import get_config
mongodb_settings = {
    'MONGODB_URL':get_config('db','MONGODB_URL'),
    'MONGODB_DB': get_config('db','MONGODB_DB'),
    'MONGODB_BATCH_SIZE': get_config('db','MONGODB_BATCH_SIZE'),
}

mongodb = MongoDBClient(mongodb_settings)
data = {}
data['usdts'] = mongodb.find_sort_limit(collection='gate_data',query={'param':'tradeHistory-btm_usdt'},
                                sort={'time':-1},limit=30,get_data=True)
data['mk_usdt'] = mongodb.find_sort_limit(collection='gate_data',query={'param':'marketlist-btm_usdt'},
                                              sort={'time':-1},limit=1,get_data=True)
if data['mk_usdt']:
    data['mk_usdt'] = data['mk_usdt'][0]
print(1)