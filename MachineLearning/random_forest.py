#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: random_forest.py
@time: 2019/5/14 014 15:46
@desc:
    随机森林算法实现
'''
import pandas as pd
from config.config import get_config
from sklearn.ensemble import RandomForestClassifier

def Predict(X):
    '''

    :param X: 预测向量
    :return: 预测结果
    '''
    # n_estimators=100 设置决策树个数为100 , 样本输入为 2个特征，因此设置max_features = 2
    model = RandomForestClassifier(n_estimators=100,
                                   bootstrap=True,
                                   max_features=2)
    train_set_path = get_config('TRAINING','TRAINING_SAVE_PATH') + get_config('TRAINING','TRAINING_SET_NAME')
    train_labels_path = get_config('TRAINING','TRAINING_SAVE_PATH') + get_config('TRAINING','TRAINING_LABELS_NAME')

    train_set = pd.read_csv(train_set_path, header=0, sep=' ')[['amount_sum', 'counts']]
    train_labels = pd.read_csv(train_labels_path, header=0, sep=' ')['status']

    # 进行训练
    model.fit(train_set, train_labels)

    # 返回预测结果
    return model.predict(X)