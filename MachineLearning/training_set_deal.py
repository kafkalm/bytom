#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: training_set_deal.py
@time: 2019/5/15 015 17:27
@desc:
    对训练集进行处理
'''

import pandas as pd
import numpy as np
import time

# 1. 处理coinmetrics.csv , blockmeta.csv的时间戳对应关系
# coinmetrics 时间戳为每日8:00 , 将blockmeta的时间戳 用 超过8:00则算下一日 未超过8:00则算前一日的方法处理
def time_deal(t):
    '''

    :param t: timestamp
    :return: timestamp
    '''
    # 格式化时间戳
    a = time.localtime(t)
    b = time.strftime('%Y-%m-%d 08:00:00', a)
    b = time.strptime(b, '%Y-%m-%d %H:%M:%S')
    if a.tm_hour >=8 :
        b = time.mktime(b) + 86400
    else:
        b = time.mktime(b)
    return int(b)

# 2. 生成训练集对应的label
def gen_label(df):
    '''

    :param df: DataFrame(coinmetrics)
    :return: DataFrame
    '''
    labels = pd.DataFrame(np.zeros(df.shape), index=None, columns=['time', 'status'])
    for i in range(1, df.shape[0]):
        if df['price'][i] > df['price'][i - 1]:
            labels['status'][i] = '+'
        elif df['price'][i] < df['price'][i - 1]:
            labels['status'][i] = '-'
        else:
            labels['status'][i] = '/'
    return labels

# 3. 统计blockmeta每个时间戳的大额交易量与交易数
def statistics(df):
    '''

    :param df: DataFrame(blockmeta)
    :return: DataFrame
    '''
    amount_sum = df.groupby(by='time')['amount'].sum()
    counts = df['time'].value_counts()
    result = pd.concat([amount_sum,counts],axis=1,ignore_index=True)
    result['time'] = result.index
    result.columns = ['amount_sum','counts','time']
    result.sort_values('time',inplace=True)
    return result

# 4. 将统计量训练集 与 Labels 的时间戳同步
def sync(df1,df2):
    '''

    :param df1: DataFrame(coinmetrics)
    :param df2: DataFrame(blockmeta)
    :return:
    '''
    df1.set_index('time',inplace=True)
    df2.set_index('time',inplace=True)
    result = pd.concat([df1,df2],axis=1,join_axes=[df2.index])
    result['time'] = result.index
    return result[['time','status']]

def gen_X(l):
    '''
    生成要预测的向量
    :param l: list
    :return: [amount_sum,count]
    '''
    amount_sum = []
    for i in range(len(l)):
        if l[i].get('data').get('transaction_amount') >= 100000000*100000:
            amount_sum.append(l[i].get('data').get('transaction_amount'))
    return [sum(amount_sum),len(amount_sum)]
