# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


import requests
from pyquery import PyQuery as pq


def is_in_baidu(key):
    for page in range(0, 1):
        url = u"http://www.baidu.com/s?wd=" + key + "&pn=" + \
            str(page) + u"&oq=" + key + "&tn=63090008_1_hao_pg&ie=utf-8&usm=2"
        rep = requests.get(url)
        text = rep.text

        jq = pq(text)
        text = jq('#content_left').html()
        if key in text:
            return True
    return False


def auto_publish_article(key):
    url = 'http://weixin.sogou.com/weixin?query=' + key + '&type=2&ie=utf8&page=' + '0' + '&p=40040100&dp=1&w=01019900&dr=1'
    rep = requests.get(url)
    text = rep.text
    jq = pq(text)
    lst_articles = jq('.wx-rb3')
    # print lst_articles, type(lst_articles), len(lst_articles)
    for article in lst_articles:
        print article
        # alinks = article.find("div")[0]
        # print len(alinks)
        # print dir(alinks)
        # print alinks
        # print alinks.text
        break

    # print is_in_baidu(u'金融信息的过滤与整合，还您一个客观真实的金融景象')


if __name__ == '__main__':
    key = u'原创 股票'
    auto_publish_article(key)
