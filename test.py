#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: test.py
@time: 2019/5/10 010 15:43
@desc:
'''
from db.MongoDB import MongoDBClient
from pymongo import UpdateOne
from pymongo import MongoClient
mongodb_settings = {
'MONGODB_URL' : 'mongodb://localhost:27017/',
    'MONGODB_DB' : 'bytom',
    'MONGODB_BATCH_SIZE':1000
}

mongodb = MongoDBClient(mongodb_settings)
#1557878400
results = mongodb.find(collection='blockmeta_data',query={"timestamp":{"$gt":1553878400,"$lte":1557878400}})
with open('D:\\bytom\\TrainingSet\\test.csv','a') as f:
    count = 0
    for result in results:
        if result.get('data').get('transaction_amount') >= 100000000*100000:
            f.write(str(result.get('timestamp'))+' '+str(result.get('data').get('transaction_amount')) + '\n')
            count += 1
            print("已插入%d条" % count)
mongodb._close()
# mongodb = MongoClient('mongodb://localhost:27017/')
# db = mongodb['bytom']
# result = db.seeds.find({})
# for _ in result:
#     print(_)