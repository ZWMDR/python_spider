# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 15:53:03 2019

@author: ZWMDR
"""

import json
from pyecharts import Bar,Line,EffectScatter
import math
import numpy as np

def load_jsons(movies):
    sentiments=[]
    for movie in movies:
        path=movie+"sentiments.json"
        file=open(path,"r",encoding='utf-8')
        sentiment=json.loads(file.read())
        file.close()
        sentiments.append(sentiment)
    return sentiments

def integrate_dict(sentiments,attr):
    data={}
    for figure in attr:
        data[figure]=[]
    for sentiment in sentiments:
        for figure in attr:
            for sent in sentiment[figure]:
                data[figure].append(sent)
    return data

def reanalyze(data,attr):
    re_data={}.fromkeys(attr,0)
    re_data_NLP={}.fromkeys(attr,0)
    re_data_disp={}.fromkeys(attr,0)
    re_data_c={}.fromkeys(attr,0)
    count=0
    for figure in attr:
        score=0
        amount=len(data[figure])
        count+=amount
        for item in data[figure]:
            score+=item[0]
        re_data_NLP[figure]=round(score/amount,4)
        re_data[figure]=amount
    for figure in attr:
        re_data[figure]/=count
        re_data[figure]=round(re_data[figure],4)
    
    for figure in attr:
        score=0
        for item in data[figure]:
            score+=(re_data_NLP[figure]-item[0])**2
        score/=count
        score=math.sqrt(score)
        re_data_disp[figure]=round(score,4)
    
    max_conc=max([score for score in re_data.values()])
    max_NLP=max([score for score in re_data_NLP.values()])
    max_disp=max([score for score in re_data_disp.values()])
    for figure in attr:
        re_data_c[figure]=round(0.75*re_data_NLP[figure]/max_NLP 
                               + 0.15*re_data[figure]/max_conc
                               + 0.1*(max_disp-re_data_disp[figure])/max_disp,4)
    
    sorted_data=sorted(re_data.items(),key=lambda x:x[1],reverse=True)
    sorted_data_NLP=sorted(re_data_NLP.items(),key=lambda x:x[1],reverse=True)
    sorted_data_disp=sorted(re_data_disp.items(),key=lambda x:x[1],reverse=True)
    sorted_data_c=sorted(re_data_c.items(),key=lambda x:x[1],reverse=True)
    
    return sorted_data,sorted_data_NLP,sorted_data_disp,sorted_data_c
    
def multi_analyze(data,attr):
    data,data_NLP,data_disp,data_c=reanalyze(data,attr)
    
    bar=Bar('观众支持率综合排行榜单', '数据来源：猫眼电影', title_pos='center', width=1200, height=600,background_color='white')
    attr,value=bar.cast(data_NLP)
    upper=max(value)
    floor=min(value)
    bar.add('', attr, value, is_visualmap=True, visual_range=[floor,upper], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./综合人物支持率-柱状图.html')
    print("综合观众支持率排行榜单已完成")
    
    bar=Bar('观众关注率综合排行榜单', '数据来源：猫眼电影', title_pos='center', width=1200, height=600,background_color='white')
    attr,value=bar.cast(data)
    upper=max(value)
    floor=min(value)
    bar.add('', attr, value, is_visualmap=True, visual_range=[floor,upper], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./综合人物关注率-柱状图.html')
    print("综合观众关注率排行榜单已完成")
    
    bar=Bar('观众情感倾向离散度综合排行榜单', '数据来源：猫眼电影', title_pos='center', width=1200, height=600,background_color='white')
    attr,value=bar.cast(data_disp)
    upper=max(value)
    floor=min(value)
    bar.add('', attr, value, is_visualmap=True, visual_range=[floor,upper], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./综合人物情感倾向离散度-柱状图.html')
    print("综合观众情感倾向离散度排行榜单已完成")
    
    bar=Bar('谁是观众心目中的最强C位？', '数据来源：猫眼电影', title_pos='center', width=1200, height=600,background_color='white')
    attr,value=bar.cast(data_c)
    upper=max(value)
    floor=min(value)
    bar.add('', attr, value, is_visualmap=True, visual_range=[floor,upper], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./最强C位-柱状图.html')
    print("最强C位综合排行榜单已完成")

def horizental_analyze(movies,attr):
    counts={}
    dispers={}
    sentiments={}
    for movie in movies:
        path=movie+"sentiments.json"
        file=open(path,"r",encoding='utf-8')
        sentiment=json.loads(file.read())
        file.close()
        st={}.fromkeys(attr,0)
        count={}.fromkeys(attr,0)
        disper={}.fromkeys(attr,0)
        for figure in attr:
            count[figure]=len(sentiment[figure])
            for item in sentiment[figure]:
                st[figure]+=item[0]
            if len(sentiment[figure])>0:
                st[figure]=round(st[figure]/len(sentiment[figure]),4)
        sentiments[movie]=st
        counts[movie]=count
        
        for figure in attr:
            for item in sentiment[figure]:
                disper[figure]+=(item[0]-st[figure])**2
        dispers[movie]=disper
    
    sum_counts={}.fromkeys(movies,0)
    for figure in attr:
        for movie in movies:
            sum_counts[movie]+=counts[movie][figure]
    
    figures_NLP={}
    figures_con={}
    figures_disp={}
    for figure in attr:
        NLP={}.fromkeys(movies,0)
        con={}.fromkeys(movies,0)
        disp={}.fromkeys(movies,0)
        for movie in movies:
            NLP[movie]=sentiments[movie][figure]
            con[movie]=round(counts[movie][figure]/sum_counts[movie],4)
            disp[movie]=round(math.sqrt(dispers[movie][figure]/sum_counts[movie]),4)
        figures_NLP[figure]=NLP
        figures_con[figure]=con
        figures_disp[figure]=disp
    
    """
    for figure in attr:
        bar=Bar("\""+figure+'\"观众感情倾向变化趋势', '数据来源：猫眼电影',title_pos='center',
                title_top='top',width=1200,height=560,background_color='white')
        
        items=[]
        values=[]
        for movie in movies:
            items.append(movie)
            values.append(figures_NLP[figure][movie])
        
        upper=max(values)
        floor=min(values)
        bar.add("",items,values, is_visualmap=True,visual_range=[floor,upper],
                xaxis_rotate=45,visual_text_color='#fff',is_more_utils=True, 
                is_label_show=True,xaxis_margin=5,xaxis_label_textsize=10,
                xaxis_type="category")

        bar.render('./'+figure+'人物支持率变化趋势-柱状图.html')
        
        bar=Bar("\""+figure+'\"观众关注度变化趋势', '数据来源：猫眼电影',title_pos='center',
                title_top='top',width=1200,height=560,background_color='white')
        items=[]
        values=[]
        for movie in movies:
            items.append(movie)
            values.append(figures_con[figure][movie])
        
        upper=max(values)
        floor=min(values)
        bar.add("",items,values, is_visualmap=True,visual_range=[floor,upper],
                xaxis_rotate=45,visual_text_color='#fff',is_more_utils=True, 
                is_label_show=True,xaxis_margin=5,xaxis_label_textsize=10,
                xaxis_type="category")

        bar.render('./'+figure+'人物关注度变化趋势-柱状图.html')
        
        
        bar=Bar("\""+figure+'\"观众情感倾向离散度变化趋势', '数据来源：猫眼电影',title_pos='center',
                title_top='top',width=1200,height=560,background_color='white')
        
        items=[]
        values=[]
        for movie in movies:
            items.append(movie)
            values.append(figures_disp[figure][movie])
        
        upper=max(values)
        floor=min(values)
        bar.add("",items,values, is_visualmap=True,visual_range=[floor,upper],
                xaxis_rotate=45,visual_text_color='#fff',is_more_utils=True, 
                is_label_show=True,xaxis_margin=5,xaxis_label_textsize=10,
                xaxis_type="category")

        bar.render('./'+figure+'人物情感倾向离散度变化趋势-柱状图.html')
    """
    
    
    re_attr=["灭霸","美国队长", "钢铁侠", "绿巨人", "奇异博士",  "蜘蛛侠", "雷神",
            "黑寡妇", "鹰眼", "惊奇队长", "幻视","猩红女巫","蚁人", "古一法师","星云"]
    
    re_movies=["《复仇者联盟》","《复仇者联盟2》","《复仇者联盟3：\n无限战争》","《复仇者联盟4：\n终局之战》",
            "《奇异博士》","《惊奇队长》","《黑豹》","《银河护卫队1》","《银河护卫队2》",
            "《蚁人1》","《蚁人2》","《雷神1》","《雷神2》","《雷神3》","《钢铁侠1》",
            "《钢铁侠2》","《钢铁侠3》","《美国队长1》","《美国队长2》","《美国队长3》"]
    for i in range(len(attr)):
        bar=Bar("\""+re_attr[i]+'\"受欢迎程度横比', '数据来源：猫眼电影',title_pos='left',
                title_top='top',width=1200,height=560,background_color='white')
        
        items=[]
        values=[]
        for k in range(len(movies)):
            items.append(re_movies[k])
            values.append(figures_NLP[attr[i]][movies[k]])
        
        upper=max(values)
        floor=min(values)
        bar.add("观众感情倾向变化趋势",items,values, is_visualmap=False,visual_range=[floor,upper],
                xaxis_rotate=45,visual_text_color='#fff',is_more_utils=True, 
                is_label_show=True,xaxis_margin=5,xaxis_label_textsize=11,
                xaxis_type="category")
        
        items=[]
        values=[]
        for k in range(len(movies)):
            items.append(re_movies[k])
            values.append(figures_disp[attr[i]][movies[k]])
        
        upper=max(values)
        floor=min(values)
        bar.add("观众感情倾向离散度",items,values, is_visualmap=False,visual_range=[floor,upper],
                xaxis_rotate=45,visual_text_color='#fff',is_more_utils=True, 
                is_label_show=True,xaxis_margin=5,xaxis_label_textsize=11,
                xaxis_type="category")
        
        items=[]
        values=[]
        for k in range(len(movies)):
            items.append(re_movies[k])
            values.append(figures_con[attr[i]][movies[k]])
        
        upper=max(values)
        floor=min(values)
        bar.add("观众关注度",items,values, is_visualmap=False,visual_range=[floor,upper],
                xaxis_rotate=45,visual_text_color='#fff',is_more_utils=True, 
                is_label_show=True,xaxis_margin=5,xaxis_label_textsize=11,
                xaxis_type="category")
        bar.render('./'+re_attr[i]+'受欢迎程度横比-柱状图.html')
        
    print("人物支持率变化趋势表已完成")
    
if __name__=="__main__":
    movies=["《复仇者联盟》","《复仇者联盟2》","《复仇者联盟3：无限战争》","《复仇者联盟4：终局之战》",
            "《奇异博士》","《惊奇队长》","《黑豹》","《银河护卫队1》","《银河护卫队2》",
            "《蚁人1》","《蚁人2》","《雷神1》","《雷神2》","《雷神3》","《钢铁侠1》",
            "《钢铁侠2》","《钢铁侠3》","《美国队长1》","《美国队长2》","《美国队长3》"]
    
    attr = ["灭霸","美国队长", "钢铁侠", "浩克", "奇异博士",  "蜘蛛侠", "索尔",
            "黑寡妇", "鹰眼", "惊奇队长", "幻视","猩红女巫","蚁人", "古一法师","星云"]
    
    sentiments=load_jsons(movies)
    data=integrate_dict(sentiments,attr)
    #multi_analyze(data,attr)
    movies=["《复仇者联盟》","《钢铁侠3》","《银河护卫队1》","《美国队长2》","《复仇者联盟2》",
            "《蚁人1》","《美国队长3》","《奇异博士》","《银河护卫队2》","《黑豹》","《复仇者联盟3：无限战争》",
            "《惊奇队长》","《蚁人2》","《复仇者联盟4：终局之战》"]
    
    horizental_analyze(movies,attr)
    
    
    