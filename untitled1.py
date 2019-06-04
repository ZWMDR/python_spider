# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 23:59:19 2019

@author: ZWMDR
"""

from snownlp import SnowNLP

string1='我超爱学习python的'
string2='我疯了'

print(SnowNLP(string1).sentiments)
print(SnowNLP(string2).sentiments)
