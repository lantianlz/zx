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
        # print i
        # if i < 800:
        #     continue
        url = "http://yahoo.compass.cn/stock/frames/frmHistoryDetail.php?code=%s%s" % (["sh", "sz"][stock.belong_market], stock.code)
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
            if not StockData.objects.filter(stock=stock, date=date):
                StockData.objects.create(stock=stock, date=date, open_price=open_price, high_price=high_price,
                                         low_price=low_price, close_price=close_price, volume=volume, turnover=turnover)

        if i % 100 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)
        # break
    print 'ok'


def update_stock_data():
    for stock_data in StockData.objects.select_related("stock").all():
        stock_data_pre = StockData.objects.filter(stock=stock_data.stock, date__lt=stock_data.date)[:1]
        print stock_data_pre
        break

if __name__ == '__main__':
    # init_stock_data()
    update_stock_data()
