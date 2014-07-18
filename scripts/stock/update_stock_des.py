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
import re
from pprint import pprint
from pyquery import PyQuery as pq

from www.stock.models import Stock


def update_stock_des():
    def _replace_html_tag(text):
        tag_s = re.compile('<[^\/]+?>')
        tag_e = re.compile('</\w+?>')
        tag_se = re.compile('<\w+?/>')
        text = tag_s.sub('', text)
        text = tag_e.sub(' ', text)
        text = tag_se.sub(' ', text)
        return text

    total = 0
    for stock in Stock.objects.filter(des=None).order_by("code"):
        url = "http://xueqiu.com/S/%s%s" % (["SH", "SZ"][stock.belong_market], stock.code)
        resp = requests.get(url)
        text = resp.text

        jq = pq(text)
        infos = jq('.stock-company .companyInfo')
        j = len(infos) - 1
        i = j - 1
        try:
            des = _replace_html_tag(jq('.stock-company .companyInfo:eq(%s)' % i).html()).replace(u"简介:", "").replace(u"收起", "").strip()
            main_business = _replace_html_tag(jq('.stock-company .companyInfo:eq(%s)' % j).html()).replace(u"业务:", "").strip()
        except Exception, e:
            print e
            print (u"error:%s\nurl is:%s" % (stock.name, url)).encode("utf8")
            continue

        # print des.encode("utf8")
        # print main_business.encode("utf8")

        # break

        stock.des = des
        stock.main_business = main_business
        stock.save()
        total += 1
        if total % 100 == 0:
            print u"%s complete" % total
    print 'ok'


if __name__ == '__main__':
    update_stock_des()
