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
import datetime
from pyquery import PyQuery as pq
from www.stock.models import Stock, StockData


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"}


def init_stock_data():
    for i, stock in enumerate(Stock.objects.all().order_by("code")):
        # print i, stock.id
        for page in range(1, 9):
            url = "http://yahoo.compass.cn/stock/frames/frmHistoryDetail.php?code=%s%s&page=%s" % (["sh", "sz"][stock.belong_market], stock.code, page)
            # print url
            for j in range(3):
                try:
                    resp = requests.get(url, timeout=10, headers=headers)
                    break
                except Exception, e:
                    print stock, stock.id
                    print e

            if not resp.status_code == 200:
                continue
            resp.encoding = "utf8"
            text = resp.text

            jq = pq(text)
            trs = jq(".table-style1 tbody tr")
            for tr in trs:
                tr = jq(tr)
                date = tr("th").html()
                open_price = tr("td:eq(0)").html()
                high_price = tr("td:eq(1)").html()
                low_price = tr("td:eq(2)").html()
                close_price = tr("td:eq(3)").html()
                volume = tr("td:eq(4)").html()
                turnover = tr("td:eq(5)").html()

                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                volume = float(volume.replace(",", "")) * 10000
                turnover = float(turnover.replace(",", "")) * 10000

                # print date, open_price, high_price, low_price, close_price, volume, turnover
                if date < datetime.datetime.strptime("2014-01-01", "%Y-%m-%d"):
                    continue
                if not StockData.objects.filter(stock=stock, date=date):
                    StockData.objects.create(stock=stock, date=date, open_price=open_price, high_price=high_price,
                                             low_price=low_price, close_price=close_price, volume=volume, turnover=turnover)
                else:
                    pass

        if i % 100 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)
        # break
    print 'ok'


def get_stock_total_by_day():
    from django.db.models import Sum
    from common.raw_sql import exec_sql

    dates = exec_sql("select distinct(date) from stock_stockdata")
    dates = [d[0] for d in dates]
    stock_total = {}
    for d in dates:
        stock_total[d] = StockData.objects.filter(date=d).aggregate(Sum('turnover'))['turnover__sum']

    return stock_total


def update_stock_turnover_rate_to_all():
    dict_stock_total = get_stock_total_by_day()
    i = 0
    for stock_data in StockData.objects.all():
        if dict_stock_total.get(stock_data.date):
            stock_data.turnover_rate_to_all = stock_data.turnover / dict_stock_total.get(stock_data.date)
            stock_data.save()
        if i % 1000 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)
        i += 1
        # break


def update_stock_turnover_change():
    i = 0
    for stock_data in StockData.objects.filter(turnover_change_pre_day=0).order_by("id"):
        i += 1
        stock_data_pres = StockData.objects.filter(stock=stock_data.stock, date__lt=stock_data.date)[:1]
        if stock_data_pres:
            stock_data_pre = stock_data_pres[0]

            if stock_data_pre.turnover > 0 and stock_data.turnover > 0:
                turnover_change_pre_day = (stock_data.turnover - stock_data_pre.turnover) / stock_data_pre.turnover * 100
                stock_data.turnover_change_pre_day = turnover_change_pre_day

            if stock_data_pre.turnover_rate_to_all > 0 and stock_data.turnover_rate_to_all > 0:
                turnover_rate_to_all_change_per_day = (stock_data.turnover_rate_to_all - stock_data_pre.turnover_rate_to_all) / stock_data_pre.turnover_rate_to_all * 100
                stock_data.turnover_rate_to_all_change_per_day = turnover_rate_to_all_change_per_day

            stock_data.save()
        if i % 1000 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)
        # break


if __name__ == '__main__':
    # init_stock_data()
    # update_stock_turnover_rate_to_all()
    update_stock_turnover_change()
