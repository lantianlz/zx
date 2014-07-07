# -*- coding: utf-8 -*-

import requests


def touch_baidu(key):
    for page in range(20000, 30000, 10):
        print page
        url = u"http://www.baidu.com/s?wd=" + key + "&pn=" + \
            str(page) + u"&oq=" + key + "&tn=63090008_1_hao_pg&ie=utf-8&usm=2"
        rep = requests.get(url)
        text = rep.text
        if "zhixuan" in text or u"智选" in text:
            print u"page num is %s" % page
            break
    print rep.text.encode('utf8')

if __name__ == '__main__':
    key = u"成都股票开户"
    touch_baidu(key)
