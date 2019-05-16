#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: panda_deal.py
@time: 2019/5/15 015 15:54
@desc:
'''
import pandas as pd
import numpy as np
from MachineLearning import training_set_deal as tr
df1 = pd.read_csv('D:\\bytom\\TrainingSet\\test.csv',header=None,sep=' ')
# df2 = pd.read_csv('D:\\bytom\\TrainingSet\\training_set_100w.csv',header=0,sep=' ')
# out = tr.sync(df1,df2)
out0 = df1[0].count()
out1 = df1[1].sum()
out = pd.DataFrame([out0,out1])
out.to_csv('D:\\bytom\\TrainingSet\\test_2.csv',sep=' ',index=False)
# labels = pd.DataFrame(np.zeros((365,2)),index=None,columns=['time','status'])
# labels['time'] = df['time']
# for i in range(1,365):
#     if df['price'][i] > df['price'][i-1]:
#         labels['status'][i] = '+'
#     elif df['price'][i] < df['price'][i-1]:
#         labels['status'][i] = '-'
#     else:
#         labels['status'][i] = '/'
# labels.to_csv('D:\\bytom\\TrainingSet\\labels.csv',sep=' ',index=False)