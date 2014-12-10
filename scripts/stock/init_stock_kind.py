# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import datetime
from www.stock.models import Stock, StockData, StockKind, Kind


def get_kind(name):
    try:
        return Kind.objects.get(name=name)
    except Kind.DoesNotExist:
        return Kind.objects.create(name=name)


def init_stock_kind():
    kind_names = []
    for i, line in enumerate(open("hangye.txt").xreadlines()):
        line = line.strip()
        try:
            line = unicode(line, "utf8")
        except:
            line = unicode(line, "gbk")

        # print i, line.encode("utf8")
        # break

        if not line or u"行业名称" in line:
            continue
        datas = line.split()
        if datas.__len__() < 3:
            continue

        kind_name, stock_code, stock_name = datas
        if kind_name not in kind_names:
            kind_names.append(kind_name)

        stocks = list(Stock.objects.filter(code=stock_code))
        if stocks:
            stock = stocks[0]
            if stock.name != stock_name:    # 更新股票名称
                print stock_name.encode("utf8"), stock.name.encode("utf8")
                stock.name = stock_name
                stock.save()

            stock_kind = get_kind(kind_name)
            if not StockKind.objects.filter(stock=stock, kind=stock_kind):
                StockKind.objects.create(stock=stock, kind=stock_kind)

    print 'ok'


if __name__ == '__main__':
    init_stock_kind()
