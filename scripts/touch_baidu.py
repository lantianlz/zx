# -*- coding: utf-8 -*-

import requests


def touch_baidu(key):
    for page in range(0, 100, 10):
        # print (page / 10 + 1)
        url = u"http://www.baidu.com/s?wd=" + key + "&pn=" + \
            str(page) + u"&oq=" + key + "&tn=63090008_1_hao_pg&ie=utf-8&usm=2"
        rep = requests.get(url)
        text = rep.text
        if "zhixuan" in text or u"智选" in text:
            # print u"page num is %s" % (page / 10 + 1)
            break
    # print rep.text.encode('utf8')
    return (page / 10 + 1)

if __name__ == '__main__':
    key = u"喀什股票开户"
    print touch_baidu(key)
