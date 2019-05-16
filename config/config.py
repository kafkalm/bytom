#!/usr/bin/env python
# encoding: utf-8
'''
@author: kafkal
@contact: 1051748335@qq.com
@software: pycharm
@file: config.py
@time: 2019/5/8 008 15:00
@desc:
'''
import configparser
import os

def get_config(section,opition):
    try:
        os.chdir(os.path.dirname(__file__))
        cf = configparser.ConfigParser()
        cf.read('settings.ini')
        return cf.get(section,opition)
    except Exception as e:
        return None
