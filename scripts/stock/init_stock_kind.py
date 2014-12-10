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
import datetime
from www.stock.models import Stock, StockData, StockKind, Kind, KindData


def get_kind(name):
    try:
        return Kind.objects.get(name=name)
    except Kind.DoesNotExist:
        return Kind.objects.create(name=name)


def init_stock_kind():
    kind_names = []
    for i, line in enumerate(open(os.path.abspath(os.path.join(SITE_ROOT, './hangye.txt'))).xreadlines()):
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


def get_all_dates():
    from common.raw_sql import exec_sql

    dates = exec_sql("select distinct(date) from stock_stockdata")
    dates = [d[0] for d in dates]
    return dates


# def get_kind_turnover(kind, date):
#     sks = StockKind.objects.filter(kind=kind)


def init_stock_kind_data():

    dates = get_all_dates()
    dict_sk = {}
    for sk in StockKind.objects.select_related("stock", "kind").all():
        dict_sk[sk.stock.id] = sk.kind

    for date in dates:
        dict_kind_trunover = {}
        sds = StockData.objects.filter(date=date)
        for sd in sds:
            if sd.stock_id not in dict_sk:
                continue
            kind = dict_sk[sd.stock_id]
            if kind in dict_kind_trunover:
                dict_kind_trunover[kind] += sd.turnover
            else:
                dict_kind_trunover[kind] = sd.turnover
        for kind in dict_kind_trunover:
            if not KindData.objects.filter(kind=kind, date=date):
                KindData.objects.create(kind=kind, date=date, turnover=dict_kind_trunover[kind])
        print u"%s: %s over" % (str(datetime.datetime.now()), str(date))


def get_kind_total_by_day():
    from django.db.models import Sum
    from common.raw_sql import exec_sql

    dates = exec_sql("select distinct(date) from stock_kinddata")
    dates = [d[0] for d in dates]
    kind_total = {}
    for d in dates:
        kind_total[d] = KindData.objects.filter(date=d).aggregate(Sum('turnover'))['turnover__sum']

    return kind_total


def update_kind_turnover_rate_to_all():
    kind_total = get_kind_total_by_day()
    # pprint(kind_total)
    for i, kind_data in enumerate(KindData.objects.select_related("kind").all()):
        if kind_total.get(kind_data.date):
            kind_data.turnover_rate_to_all = kind_data.turnover / kind_total.get(kind_data.date)
            kind_data.save()
        if i % 1000 == 0:
            print "%s:%s ok" % (datetime.datetime.now(), i)
        # break


def update_kind_turnover_change():
    for i, kind_data in enumerate(KindData.objects.select_related("kind").all()):
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


if __name__ == '__main__':
    init_stock_kind()
    init_stock_kind_data()
    update_kind_turnover_rate_to_all()
    update_kind_turnover_change()
