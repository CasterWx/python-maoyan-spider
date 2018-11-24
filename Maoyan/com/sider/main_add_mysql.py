# -*- coding: utf-8 -*-
import os
import re
import xml.dom.minidom as xmldom
import pymysql
from bs4 import BeautifulSoup
import requests
from fontTools.ttLib import TTFont

# 请求头设置
header = {
    'Accept': '*/*;',
    'Connection': 'keep-alive',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'maoyan.com',
    'Referer': 'http://maoyan.com/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}

# 下载请求电影页面的woff字体到本地
def downfont(url):
    r = requests.get('http://'+url)
    with open("demo.woff", "wb") as code:
        code.write(r.content)
    font = TTFont("demo.woff")
    font.saveXML('to.xml')


def findstar(titles):
    # 加载字体模板
    num = [8,6,2,1,4,3,0,9,5,7]
    data = []
    new_font = []
    xmlfilepath_temp = os.path.abspath("temp.xml")
    domobj_temp = xmldom.parse(xmlfilepath_temp)
    elementobj_temp = domobj_temp.documentElement
    subElementObj = elementobj_temp.getElementsByTagName("TTGlyph")
    for i in range(len(subElementObj)):
        rereobj = re.compile(r"name=\"(.*)\"")
        find_list = rereobj.findall(str(subElementObj[i].toprettyxml()))
        data.append(str(subElementObj[i].toprettyxml()).replace(find_list[0],'').replace("\n",''))

    #根据字体模板解码本次请求下载的字体
    xmlfilepath_find = os.path.abspath("to.xml")
    domobj_find = xmldom.parse(xmlfilepath_find)
    elementobj_find = domobj_find.documentElement
    tunicode = elementobj_find.getElementsByTagName("TTGlyph")
    for i in range(len(tunicode)):
        th = tunicode[i].toprettyxml()
        report = re.compile(r"name=\"(.*)\"")
        find_this = report.findall(th)
        get_code = th.replace(find_this[0], '').replace("\n", '')
        for j in range(len(data)):
            if get_code==data[j]:
                new_font.append(num[j])

    font = TTFont("demo.woff")
    font_list = font.getGlyphNames()
    font_list.remove('glyph00000')
    font_list.remove('x')
    for i in range(len(font_list)) :
        font_list[i] = str(font_list[i]).lower().replace("uni",'')

    return (new_font,font_list)


def web(url):
    db_data = requests.get(url, headers=header)
    soup = BeautifulSoup(db_data.text.replace("&#x",""), 'lxml')

    titles = soup.select('body > div.banner > div > div.celeInfo-right.clearfix > div.movie-brief-container > h3')
    ename = soup.select('body > div.banner > div > div.celeInfo-right.clearfix > div.movie-brief-container > div')
    people = soup.select('body > div.banner > div > div.celeInfo-right.clearfix > div.movie-stats-container > div > div > div > span > span')
    manary = soup.select('body > div.banner > div > div.celeInfo-right.clearfix > div.movie-stats-container > div > div > span.stonefont')
    danwei = soup.select('body > div.banner > div > div.celeInfo-right.clearfix > div.movie-stats-container > div > div > span.unit')
    star = soup.select(
        'body > div.banner > div > div.celeInfo-right.clearfix > div.movie-stats-container > div > div > span > span')
    woffs = soup.select('head > style')

    # 获得字体路径
    wotflist = str(woffs[0]).split('\n')
    maoyanwotf = wotflist[5].replace(' ','').replace('url(\'//','').replace('format(\'woff\');','').replace('\')','')
    downfont(maoyanwotf)
    # 解析编码
    (new_font, font_list) = findstar(titles)

# 匹配
    #电影名
    movie_name = titles[0].get_text()
    #演员名
    ename_name = ename[0].get_text()
    try:
        #评分人数
        people_number = re.findall(re.compile(r">(.*)<"), str(people[0]))[0].replace(';','')
        for i in range(len(font_list)):
            if font_list[i] in people_number:
                people_number = str(people_number).replace(font_list[i],str(new_font[i]))
    except:
        people_number = "无人评分"

        #评分
    try:
        star_woff = re.findall(re.compile(r">(.*)<"), str(star[0]))[0].replace(';','')
        for i in range(len(font_list)):
            if font_list[i] in star_woff:
                star_woff = str(star_woff).replace(font_list[i],str(new_font[i]))
    except:
        star_woff = "暂无评分"

        #票房
    try:
        manary_number = re.findall(re.compile(r">(.*)<"), str(manary[0]))[0].replace(';','')
        for i in range(len(font_list)):
            if font_list[i] in manary_number:
                manary_number = str(manary_number).replace(font_list[i],str(new_font[i]))
        danweid = danwei[0].get_text()
        getmanary = manary_number + str(danweid)
    except:
        getmanary = "暂无票房"
        #ename_name = ename_name.encode('unicode-escape').decode('string_escape')
    # data = "\'"+str(url)+"\', \'"+str(movie_name)+"\', \'"+str(ename_name)+"\', \'"+str(people_number)+"\', \'"+str(star_woff)+"\', \'"+str(getmanary)+"\'"

    data = "\'"+str(url)+"\', \'"+str(movie_name)+"\', \'"+str(ename_name)+"\', \'"+str(people_number)+"\', \'"+str(star_woff)+"\', \'"+str(getmanary)+"\'"

    to_mysql(data)


def find_mysql():
    db= pymysql.connect(host="localhost",user="root",password="root",db="maoyan",port=3306)
    cur = db.cursor()
    sql = "select * from t_films"
    try:
        cur.execute(sql)
        results = cur.fetchall()
        print (len(results))
        for row in results:
            print(row[0]+"   "+row[1]+"  "+row[2]+"  "+row[3]+"  "+row[4]+"星   "+row[5])
    except Exception as e:
        raise e
    finally:
        db.close()


def to_mysql(data):
    '''
     create table `films`(
     `url` varchar(50) not null primary key,
     `movie` varchar(50) character set utf8 not null ,
     `ename` varchar(50) character set utf8  ,
     `people` varchar(50) character set utf8 ,
     `star` varchar(50) character set utf8 ,
     `pf` varchar(50) character set utf8 )ENGINE=InnoDB DEFAULT CHARSET=utf8;
    '''
    db = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='maoyan', charset='gbk')
    cursor = db.cursor()
    sql = 'INSERT INTO films(`url`,`movie`,`ename`,`people`,`star`,`pf`) VALUES ('+data+')'
    print(sql)
    try:
        cursor.execute(sql)
        print("Successful")
        db.commit()
    except:
        print('Failed')
        db.rollback()
    db.close()


def beginSpider():
    url_base = 'http://maoyan.com/films?showType=3&offset='
    for i in range(0, 1980, 30):
        url =  url_base + str(i)
        db_data = requests.get(url, headers=header)
        soup = BeautifulSoup(db_data.text, 'lxml')
        id = re.findall(re.compile(r"movieId:(.*)}"), str(soup))
        for i in id :
            web("http://maoyan.com/films/" + str(i))


if __name__ == '__main__':
    beginSpider()
    find_mysql()