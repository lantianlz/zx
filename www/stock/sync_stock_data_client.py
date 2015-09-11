# -*- coding: utf-8 -*-

import requests, re, json, time, datetime, traceback, random
from pyquery import PyQuery as pq

# host = "www.a.com:8000"
host = "www.zhixuan.com"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

def get_stocks():
    
    url = "http://%s/stock/get_stock_json" % host
    req = requests.get(url)
    return json.loads(req.text)

def sync():
    stocks = get_stocks()

    for stock in stocks:
        time.sleep(4)

        url = "http://hq.sinajs.cn/list=%s%s" % (stock['market'], stock['code'])

        resp = None
        for j in range(3):
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                break
            except Exception, e:
                print stock, stock.id
                print e

        if not resp or resp.status_code != 200:
            continue
        text = resp.text

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

        # 提交到服务器
        response = requests.post(
            "http://%s/stock/sync_stock_data" % host,
            data = {
                'stock_id': stock['id'],
                'date': date,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'volume': volume,
                'turnover': turnover
            }
        )

if __name__ == "__main__":
    sync()