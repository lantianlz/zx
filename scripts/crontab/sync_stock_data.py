# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from pprint import pprint
import requests
import datetime
from pyquery import PyQuery as pq
from www.stock.models import Stock, StockData, KindData, StockKind


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"}


def sync_stock_data():
    for i, stock in enumerate(Stock.objects.all().order_by("code")):
        url = "http://hq.sinajs.cn/list=%s%s" % (["sh", "sz"][stock.belong_market], stock.code)
        for j in range(3):
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                break
            except Exception, e:
                print stock, stock.id
                print e

        if not resp.status_code == 200:
            continue
        text = resp.text
        # pprint(datas)
        # print text.encode("utf8")

        datas = text.split('="')[1].split('"')[0].split(',')
        if len(datas) < 3:
            continue
        date = datetime.datetime.strptime(datas[-3], "%Y-%m-%d").date()
        open_price = datas[1]
        high_price = datas[4]
        low_price = datas[5]
        close_price = datas[3]
        volume = datas[8]
        turnover = datas[9]

        if date < datetime.datetime.now().date() or float(turnover) < 100:
            continue
        # print date, open_price, high_price, low_price, close_price, volume, turnover
        sds = list(StockData.objects.filter(stock=stock, date=date))
        if not sds:
            StockData.objects.create(stock=stock, date=date, open_price=open_price, high_price=high_price,
                                     low_price=low_price, close_price=close_price, volume=volume, turnover=turnover)
        else:
            sd = sds[0]
            ps = dict(open_price=open_price, high_price=high_price,
                      low_price=low_price, close_price=close_price, volume=volume, turnover=turnover)
            for key in ps:
                setattr(sd, key, ps[key])
            sd.save()

        if i % 100 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)
        # break
    print 'ok'


now_date = datetime.datetime.now().date()


def get_stock_total_today():
    from django.db.models import Sum
    stock_total = {}
    stock_total[now_date] = StockData.objects.filter(date=now_date).aggregate(Sum('turnover'))['turnover__sum']
    return stock_total


def update_stock_turnover_rate_to_all_today():
    dict_stock_total = get_stock_total_today()
    for i, stock_data in enumerate(StockData.objects.select_related("stock").filter(date=now_date)):
        if dict_stock_total.get(stock_data.date):
            stock_data.turnover_rate_to_all = stock_data.turnover / dict_stock_total.get(stock_data.date)
            stock_data.save()
        if i % 1000 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)
        # break


def update_stock_turnover_change_today():
    for i, stock_data in enumerate(StockData.objects.select_related("stock").filter(date=now_date)):
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


def update_kind_data():
    def _init_stock_kind_data():
        dict_sk = {}
        for sk in StockKind.objects.select_related("stock", "kind").all():
            dict_sk[sk.stock.id] = sk.kind

        dict_kind_trunover = {}
        sds = StockData.objects.filter(date=now_date)
        for sd in sds:
            if sd.stock_id not in dict_sk:
                continue
            kind = dict_sk[sd.stock_id]
            if kind in dict_kind_trunover:
                dict_kind_trunover[kind] += sd.turnover
            else:
                dict_kind_trunover[kind] = sd.turnover
        for kind in dict_kind_trunover:
            if not KindData.objects.filter(kind=kind, date=now_date):
                KindData.objects.create(kind=kind, date=now_date, turnover=dict_kind_trunover[kind])
        print u"%s: %s over" % (str(datetime.datetime.now()), str(now_date))

    def _get_kind_total_by_day():
        from django.db.models import Sum
        kind_total = {}
        kind_total[now_date] = KindData.objects.filter(date=now_date).aggregate(Sum('turnover'))['turnover__sum']

        return kind_total

    def _update_kind_turnover_rate_to_all_today():
        kind_total = _get_kind_total_by_day()
        # pprint(kind_total)
        for i, kind_data in enumerate(KindData.objects.select_related("kind").filter(date=now_date)):
            if kind_total.get(kind_data.date):
                kind_data.turnover_rate_to_all = kind_data.turnover / kind_total.get(kind_data.date)
                kind_data.save()
            if i % 1000 == 0:
                print "%s:%s ok" % (datetime.datetime.now(), i)
            # break

    def _update_kind_turnover_change_today():
        for i, kind_data in enumerate(KindData.objects.select_related("kind").filter(date=now_date)):
            kind_data_pres = KindData.objects.filter(kind=kind_data.kind, date__lt=kind_data.date)[:1]
            if kind_data_pres:
                kind_date_pre = kind_data_pres[0]

                if kind_date_pre.turnover > 0 and kind_data.turnover > 0:
                    turnover_change_pre_day = (kind_data.turnover - kind_date_pre.turnover) / kind_date_pre.turnover * 100
                    kind_data.turnover_change_pre_day = turnover_change_pre_day

                if kind_date_pre.turnover_rate_to_all > 0 and kind_data.turnover_rate_to_all > 0:
                    turnover_rate_to_all_change_per_day = (kind_data.turnover_rate_to_all - kind_date_pre.turnover_rate_to_all) / kind_date_pre.turnover_rate_to_all * 100
                    kind_data.turnover_rate_to_all_change_per_day = turnover_rate_to_all_change_per_day

                kind_data.save()
            if i % 1000 == 0:
                print "%s:%s ok" % (datetime.datetime.now(), i)
            # break

    _init_stock_kind_data()
    _update_kind_turnover_rate_to_all_today()
    _update_kind_turnover_change_today()


def update_stock_market_value():
    for i, stock_data in enumerate(StockData.objects.select_related("stock").filter(date=now_date)):
        stock = stock_data.stock
        url = "http://xueqiu.com/S/%s%s" % (["SH", "SZ"][stock.belong_market], stock.code)

        for j in range(3):
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                break
            except Exception, e:
                print stock, stock.id
                print e
        text = resp.text

        jq = pq(text)
        try:
            data = jq('.seperateBottom td:eq(1) span')
            market_value = float(data.html().replace(u"亿", ""))
            stock_data.market_value = market_value
            stock_data.save()
        except Exception, e:
            print e
            print url

        if i % 100 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)


if __name__ == '__main__':
    sync_stock_data()
    update_stock_turnover_rate_to_all_today()
    update_stock_turnover_change_today()
    update_kind_data()
    update_stock_market_value()
