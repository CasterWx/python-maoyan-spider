# -*- coding: utf-8 -*-
import os
import re
import xml.dom.minidom as xmldom
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
            if not cmp(get_code,data[j]):
                new_font.append(num[j])

    font = TTFont("demo.woff")
    font_list = font.getGlyphNames()
    font_list.remove('glyph00000')
    font_list.remove('x')

    # 匹配
    star_woff = re.findall(re.compile(r">(.*)<"), str(titles[0]))[0].replace(';','').split('.')
    for i in star_woff:
        getthis = i.upper()
        for j in range(len(font_list)):
            if not cmp(getthis,font_list[j].replace("uni","")):
                print(new_font[j])


def web(url):
    db_data = requests.get(url, headers=header)
    soup = BeautifulSoup(db_data.text.replace("&#x",""), 'lxml')

    titles = soup.select(
        'body > div.banner > div > div.celeInfo-right.clearfix > div.movie-stats-container > div > div > span > span')
    wotfs = soup.select('head > style')

    wotflist = str(wotfs[0]).split('\n')
    maoyanwotf = wotflist[5].replace(' ','').replace('url(\'//','').replace('format(\'woff\');','').replace('\')','')

    downfont(maoyanwotf)

    findstar(titles)


def setCsv():
    url = 'http://maoyan.com/films/42964'
    web(url)


if __name__ == '__main__':
    setCsv()  # str为标签名
