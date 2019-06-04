# -*- coding: utf-8 -*-
"""
Created on Thu May 30 09:42:35 2019

@author: ZWMDR
"""

import json
import pandas as pd
from collections import Counter
import re

filename = "./captain2_comments.csv"
titles = ['nickName','cityName','content','score','startTime']
file_name="C:\\Users\\ZWMDR\\Anaconda3\\Lib\\site-packages\\pyecharts\\datasets\\city_coordinates.json"
try:
    file=open(file_name,"r",encoding='utf-8')
except:
    print("open error")
    exit()

city=json.loads(file.read())
file.close()
comments=pd.read_csv(filename, names=titles, encoding='utf-8',lineterminator='\n')
city_name=comments['cityName'].dropna()
data = Counter(city_name).most_common(300)

for place in data:
    if place[0] not in city:
        find=False
        #json中找不到
        for name in city.keys():
            items=re.findall(place[0],name)
            if len(items)>0:
                print("find match:",place[0],"-->",name)
                city[place[0]]=city[name]
                city.pop(name)
                find=True
                break
        if not find:
            print("Not mathch",place[0])
    else:
        find=True
        

file=open(file_name,"w",encoding='utf-8')
file.write(json.dumps(city,ensure_ascii=False))
file.close()
