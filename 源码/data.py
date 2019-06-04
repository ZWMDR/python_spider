import pandas as pd
from collections import Counter
from pyecharts import Map, Geo, Bar, Line
import jieba
import jieba.analyse
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
from PIL import Image
import numpy as np
import re
from snownlp import SnowNLP
import json
import multiprocessing
import time


#读取csv文件数据 
def read_csv(filename, titles):
    comments = pd.read_csv(filename, names=titles, encoding='utf-8',lineterminator='\n')
    return comments

#观众地域图 
def draw_map(movie,comments):
    try:
        attr = comments['cityName'].dropna()
        data = Counter(attr).most_common(300)
        
        geo = Geo(movie+"全国观众地域分布", "数据来源：猫眼电影", title_color="#fff", title_pos="center", width=1000, height=600, background_color='#404a59')
        attr, value = geo.cast(data)
        geo.add("", attr, value, visual_range=[0, 1000], maptype='china',visual_text_color="#fff", symbol_size=10, is_visualmap=True)
        geo.render("./"+movie+"观众地域分布-地理坐标图.html")
        geo
        print(movie+"全国观众地域分布已完成")
    except Exception as e:
        print(e)

def draw_bar(movie,comments):
    data_top20 = Counter(comments['cityName'].dropna()).most_common(20)
    bar = Bar(movie+'观众地域排行榜单', '数据来源：猫眼电影', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(data_top20)
    upper=max(value)
    if upper>1000:
        upper=1000*(upper//1000+1)
    elif upper>100:
        upper=100*(upper//100+1)
    else:
        upper=10*(upper//10+1)
    bar.add('', attr, value, is_visualmap=True, visual_range=[0, upper], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./'+movie+'观众地域排行榜单-柱状图.html')
    print(movie+"观众地域排行榜单已完成")
    
def draw_wordCloud(movie,comments):
    data = comments['content']

    comment_data = []
    print("开始分词，此处运行时间较长")
    for item in data:
        if pd.isnull(item) == False:
            comment_data.append(item)
 
    comment_after_split = jieba.cut(str(comment_data), cut_all=False)
    words = ' '.join(comment_after_split)
    
    #自定义停用词
    stopwords = STOPWORDS.copy()

    stopwords.add('一部')
    stopwords.add('这部')
    stopwords.add('一个')
    stopwords.add('没有')
    stopwords.add('什么')
    stopwords.add('有点')
    stopwords.add('不过')
    stopwords.add('但是')
    stopwords.add('还是')
    stopwords.add('感觉')  
    stopwords.add('就是')
    stopwords.add('觉得')
    stopwords.add('电影')
    stopwords.add('好看')
    stopwords.add('可以')
    stopwords.add('不错')

    alice_mask=np.array(Image.open("./背景2.jpg"))
    
    wc = WordCloud(background_color='black',font_path='C:\\Windows\\Fonts\\SIMLI.TTF',
                   scale=4, stopwords=stopwords,max_font_size=200,
                   mask=alice_mask)
    wc=wc.generate(words)
    wc.to_file("./"+movie+"WordCloud.jpg")
 
    # plt.figure(figsize=(10, 8))
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
 
def draw_DateBar(movie,comments):
    time = comments['startTime']
    timeData = []
    for t in time:
        if pd.isnull(t) == False:
            date = t.split(' ')[0]
            timeData.append(date)

    data = Counter(timeData).most_common()
    data = sorted(data, key=lambda data : data[0]) 
   
    
    bar = Bar(movie+'观众评论数量与日期的关系', '数据来源：猫眼电影', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(data)
    bar.add('', attr, value, is_visualmap=True, visual_range=[0, 3500], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./'+movie+'观众评论日期-柱状图.html')
    print(movie+"观众评论数量与日期的关系已完成")
  

def draw_TimeBar(movie,comments):
    time = comments['startTime']
    timeData = []
    for t in time:
        if pd.isnull(t) == False:
            time = t.split(' ')[1]
            hour = time.split(':')[0]
            timeData.append(hour)
 
    data = Counter(timeData).most_common()
    data = sorted(data, key=lambda data : data[0])    
    
    bar = Bar(movie+'观众评论数量与时间的关系', '数据来源：猫眼电影', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(data)
    bar.add('', attr, value, is_visualmap=True, visual_range=[0, 3500], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./'+movie+'观众评论时间-柱状图.html')
    print(movie+"观众评论数量与时间的关系已完成")


def sentiments_analyze(movie,comments):
    attr = ["灭霸","美国队长", "钢铁侠", "浩克", "奇异博士",  "蜘蛛侠", "索尔" ,
            "黑寡妇", "鹰眼", "惊奇队长", "幻视","猩红女巫","蚁人", "古一法师","星云"]
    alias = {"灭霸": ["灭霸", "Thanos","萨罗斯","灭世霸王"],
             "美国队长": ["美国队长", "美队","captain","Captain"],
             "浩克": ["浩克", "绿巨人", "班纳", "HULK","hulk"],
             "奇异博士": ["奇异博士", "医生","斯特兰奇","博士","strange"],
             "钢铁侠": ["钢铁侠", "stark", "斯塔克", "托尼", "史塔克","iron","Iron","铁人"],
             "蜘蛛侠": ["蜘蛛侠","蜘蛛","彼得", "荷兰弟"],
             "索尔":["索尔", "雷神"],
             "黑寡妇": ["黑寡妇", "寡姐"],
             "鹰眼":["鹰眼","克林顿","巴顿","克林特"],
             "惊奇队长":["惊奇队长","卡罗尔", "惊奇"],
             "幻视":["幻视"],
             "星云":["星云"],
             "猩红女巫": ["猩红女巫", "绯红女巫", "旺达"],
             "蚁人":["蚁人", "蚁侠", "Ant", "AntMan"],
             "古一法师": ["古一", "古一法师", "法师"]}
    sentiment={}
    SENTIMENT={}
    figure={}.fromkeys(attr,0)

    for att in attr:
        sentiment[att]=[0,0]
        SENTIMENT[att]=[]
    
    data = comments['content']
    data=np.array(data)
    print("data_len:",len(data))
    print("正在计算情感倾向，此处耗时较长")
    
    
    for i in range(len(data)):
        data[i]=str(data[i])
    
    start_time=time.time()
    
    #遍历每个人物的名称
    for item in data:
        judge={}.fromkeys(attr,False)
        for cha in attr:
            for figure_name in alias[cha]:
                items=re.findall(figure_name,item)
                length=len(items)
                figure[cha]+=length
                if length>0:
                    judge[cha]=True
    
        for cha in attr:
            if judge[cha]:
                s=SnowNLP(item).sentiments
                sentiment[cha][0]+=s
                sentiment[cha][1]+=1
                SENTIMENT[cha].append((s,sentiment[cha][1]))
    
    end_time=time.time()
    print("time=",end_time-start_time)
    count=sum(figure.values())
    for figure_name in figure:
        figure[figure_name]/=count
        if sentiment[figure_name][1]>0:
            sentiment[figure_name][0]/=sentiment[figure_name][1]

    #print(movie,":",count,"\n",figure.items())
    #print(movie,":\n",sentiment.items())
    """
    
    file=open(movie+"sentiments.json","r",encoding="UTF-8")
    data=json.loads(file.read())
    file.close()
    
    figure={}.fromkeys(attr,0)
    var={}.fromkeys(attr,0)
    amount=0
    for name in attr:
        figure[name]=len(data[name])
        amount+=figure[name]
        for item in data[name]:
            var[name]+=item[0]
    
    for name in attr:
        figure[name]=round(figure[name]/amount,4)
        var[name]=round(var[name]/amount,4)
            
    """
        

    bar = Bar(movie+'观众关注率排行榜单', '数据来源：猫眼电影', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(figure)
    upper=max(value)
    floor=min(value)
    bar.add('', attr, value, is_visualmap=True, visual_range=[floor,upper], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./'+movie+'人物关注率-柱状图.html')
    print(movie+"观众关注率排行榜单已完成")
    
    var={}
    for sent in sentiment.keys():
        var[sent]=sentiment[sent][0]
    bar = Bar(movie+'观众支持率排行榜单', '数据来源：猫眼电影', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(var)
    upper=max(value)
    floor=min(value)
    bar.add('', attr, value, is_visualmap=True, visual_range=[floor,upper], visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('./'+movie+'人物支持率-柱状图.html')
    print(movie+"观众支持率排行榜单已完成")
    file=open("./"+movie+"sentiments.json","w",encoding="utf-8")
    file.write(json.dumps(SENTIMENT,ensure_ascii=False))
    file.close()
    print(movie+"观众支持率JSON已更新")
    
def analyze(argv):
    name=argv[0]
    path=argv[1]
    titles = ['nickName','cityName','content','score','startTime']
    comments=read_csv(path,titles)#加载csv文件
    
    #draw_map(name,comments)#生成地理坐标图
    #draw_bar(name,comments)#生成地理位置排行榜
    #draw_DateBar(name,comments)#生成评论日期表
    #draw_TimeBar(name,comments)#生成评论数量与时间关系图
    #draw_wordCloud(name,comments)#生成词云图
    sentiments_analyze(name,comments)#情感倾向分析
    return
    
if __name__ == "__main__":
    #movies={"《星际穿越》":"./interstellar_comments.csv","《流浪地球》":"./liulangdiqiu_comments.csv"，"《老师好》":"laoshihao_comments.csv"}
    
    movies={"《复仇者联盟》":"./fulian1_comments.csv","《复仇者联盟2》":"./fulian2_comments.csv",
            "《复仇者联盟3：无限战争》":"./fulian3_comments.csv",
            "《复仇者联盟4：终局之战》":"./fulian4_comments.csv",
            "《奇异博士》":"./strange.csv","《惊奇队长》":"./marvel_comments.csv",
            "《黑豹》":"./heibao_comments.csv","《银河护卫队1》":"./galaxy1_comments.csv",
            "《银河护卫队2》":"./galaxy2.csv","《蚁人1》":"./yiren1_comments.csv",
            "《蚁人2》":"./yiren2_comments.csv","《雷神1》":"./thro1.csv",
            "《雷神2》":"./thro2.csv","《雷神3》":"./thro3.csv",
            "《钢铁侠1》":"./Iron_man_comments.csv","《钢铁侠2》":"./Iron2_comments.csv",
            "《钢铁侠3》":"./Iron3_comments.csv","《美国队长1》":"./captain1_comments.csv",
			"《美国队长2》":"./captain2_comments.csv","《美国队长3》":"./captain3_comments.csv"
			}

    """
    movies={"《复联1》":"fulian1_comments.csv","《复联2》":"fulian2_comments.csv",
            "《复联3》":"fulian3_comments.csv","《复联4》":"fulian4_comments.csv",}
    
    """
    #movies={"《复联1》":"fulian1_comments.csv"}
    
    
    #多进程并发处理多部影片，提高CPU利用率
    multiprocessing.freeze_support()
    pool=multiprocessing.Pool(processes=multiprocessing.cpu_count())
    task=[]
    for name in movies.keys():
        task.append((name,movies[name]))
    
    #多进程并发分析数据，主进程阻塞
    start_time=time.time()
    pool.map(analyze,task)
    
    pool.close()
    pool.join()

    """
    start_time=time.time()
    for movie in movies.keys():
        analyze((movie,movies[movie]))
    """
    end_time=time.time()
    
    print("time=",end_time-start_time)#输出程序运行时间
    print("全部完成")

