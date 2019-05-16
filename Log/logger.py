#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: logger.py
@time: 2019/4/22 022 14:59
@desc:
    输出日志模块
'''
import logging
import os
import time
from config.config import get_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

date = time.strftime('%Y%m%d',time.localtime(time.time()))
log_path = get_config('Log','LOG_SAVE_PATH')
log_name = log_path + date + '.log'

#将Log信息写入到文件中 INFO级别
f = logging.FileHandler(log_name,mode='w')
f.setLevel(logging.INFO)

#将Log信息输出到控制台 DEBUG级别
c = logging.StreamHandler()
c.setLevel(logging.DEBUG)

#设置Log信息格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
f.setFormatter(formatter)
c.setFormatter(formatter)

logger.addHandler(f)
logger.addHandler(c)