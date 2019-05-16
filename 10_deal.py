#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: 10_deal.py
@time: 2019/5/16 016 13:06
@desc:
'''
from MachineLearning.training_set_deal import *
import pandas as pd

# df = pd.read_csv('D:\\bytom\\TrainingSet\\test.csv',header=0,sep=' ')
# df['time'] = df['time'].apply(time_deal)
# df[['time','amount']].to_csv('D:\\bytom\\TrainingSet\\test.csv',sep=' ',index=False)

# df = pd.read_csv('D:\\bytom\\TrainingSet\\test.csv',header=0,sep=' ')
# result = statistics(df)
# result.to_csv('D:\\bytom\\TrainingSet\\training_set_10w.csv',index=False,sep=' ')

df1 = pd.read_csv('D:\\bytom\\TrainingSet\\training_set_10w.csv',header=0,sep=' ')
df2 = pd.read_csv('D:\\bytom\\TrainingSet\\training_labels_10w.csv',header=0,sep=' ')
df1.set_index(df1['time'])
df2.set_index(df2['time'])
result = pd.merge(df1,df2,how='left',on='time')[['time','status']]
result.to_csv('D:\\bytom\\TrainingSet\\result.csv',index=False,sep=' ')