# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import re
import requests
# from pprint import pprint
from www.stock.models import Stock


def get_shanghai_company():
    def _get_company_list(text):
        p = re.compile(u"<div class='companyBox'>[\s\S]+?<\\\/div>\s*<\\\/div>", re.I)
        return list(set(p.findall(text)))

    def _get_uid(text):
        p = re.compile(u" uid=(\d+)", re.I)
        return p.findall(text)[0]

    def _get_name(text):
        p = re.compile(u"title='(.+?)'", re.I)
        return p.findall(text)[0]

    def _get_img(text):
        p = re.compile(u"src='(.+?)'", re.I)
        return p.findall(text)[0]

    def _get_code(text):
        p = re.compile(u"company\/(\d+)\.", re.I)
        return p.findall(text)[0]

    for i in range(1, 32):
        url = "http://sns.sseinfo.com/allcompany.do"
        data = dict(areaId=0, code=0, order=0, page=i)
        resp = requests.post(url, data=data)
        text = resp.text

        for company in _get_company_list(text):
            uid = _get_uid(company)
            href = "http://sns.sseinfo.com/company.do?uid=%s" % uid
            name = _get_name(company)
            img = _get_img(company)
            code = _get_code(img)

            if code.startswith("60"):
                belong_board = 0
            elif code.startswith("900"):
                belong_board = 3
            else:
                belong_board = 4

            # print uid, href, name.encode("utf8"), img, code
            if not (Stock.objects.filter(name=name) or Stock.objects.filter(origin_uid=uid)):
                Stock.objects.create(name=name, origin_uid=uid, img=img, code=code, belong_board=belong_board, belong_market=0)


def get_shenzhen_company():
    def _get_company_list(text):
        p = re.compile(u'companyObject(\("[\s\S]+?"\));', re.I)
        return list(set(p.findall(text)))

    url = "http://irm.cninfo.com.cn/szse/ssgsList.html"
    resp = requests.get(url)
    resp.encoding = "utf8"  # 未指定编码，需要人为指定
    text = resp.text

    i = 0
    a = b = c = d = e = 0
    for company in _get_company_list(text):
        company = eval(company.replace("\n", ""))
        uid = code = company[0].strip()
        name = unicode(company[1].replace(" ", ""), "utf8")
        href = company[3]
        img = company[2] if "gif" in company[2] else ""

        if not (Stock.objects.filter(name=name) or Stock.objects.filter(origin_uid=uid)):
            # print name, img, href
            if code.startswith("000") or code.startswith("001"):
                belong_board = 0
                a += 1
            elif code.startswith("002"):
                belong_board = 1
                b += 1
            elif code.startswith("300"):
                belong_board = 2
                c += 1
            elif code.startswith("200"):
                belong_board = 3
                d += 1
            else:
                belong_board = 4
                e += 1
            Stock.objects.create(name=name, origin_uid=uid, img=img, code=code, belong_board=belong_board, belong_market=1)
        # else:
        #     print (u"exist a company: %s, name:%s" % (code, name)).encode("utf8")
        i += 1
    print i, a, b, c, d, e


def init_stock_company():
    get_shanghai_company()
    get_shenzhen_company()
    print 'ok'


if __name__ == '__main__':
    init_stock_company()
