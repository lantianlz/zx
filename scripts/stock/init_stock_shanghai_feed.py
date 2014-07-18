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
import re
import time
import requests
from pyquery import PyQuery as pq
from pprint import pprint
from www.stock.models import Stock, StockFeed
from www.stock import interface


def get_shanghai_feed():
    def _replace_html_tag(text):
        tag_s = re.compile('<[^\/]+?>')
        tag_e = re.compile('</\w+?>')
        text = tag_s.sub('', text)
        text = tag_e.sub(' ', text)
        return text

    def _get_time(origin_time, pre_time):
        now = datetime.datetime.now()
        pre_year = int(pre_time.strftime("%Y"))
        # pre_month = int(pre_time.strftime("%m"))

        if u"昨天" in origin_time:
            now = datetime.datetime.now()
            now_month = int(now.strftime("%m"))
            now_day = int(now.strftime("%d"))
            origin_time = origin_time.strip().replace(u"昨天", (u"%s月%s日" % (now_month, now_day - 1)))
        if u"月" in origin_time:
            # month = int(origin_time.split(u"月")[0])
            # year = pre_year if month <= pre_month else pre_year - 1
            result_time = datetime.datetime.strptime((u"%s年%s" % (pre_year, origin_time)).encode("utf8"), '%Y年%m月%d日 %H:%M')
            if result_time > pre_time:
                result_time = datetime.datetime.strptime((u"%s年%s" % (pre_year - 1, origin_time)).encode("utf8"), '%Y年%m月%d日 %H:%M')    # 前一年
            return result_time
        if u"分钟" in origin_time:
            minute = int(origin_time.split(u"分钟")[0])
            return now - datetime.timedelta(minutes=minute)
        if u"小时" in origin_time:
            hour = int(origin_time.split(u"小时")[0])
            return now - datetime.timedelta(hours=hour)

        raise Exception, (u"time error:%s" % origin_time).encode("utf8")

    start_time = time.time()
    for stock in Stock.objects.filter(belong_market=0).order_by("id"):
        stock_origin_uid = stock.origin_uid
        url = "http://sns.sseinfo.com/ajax/userfeeds.do?typeCode=company&type=11&pageSize=2000&uid=%s&page=1" % stock_origin_uid
        resp = requests.get(url)
        text = resp.text
        # print text.encode("utf8")

        jq = pq(text)
        feeds = jq('.m_feed_item')
        pre_time = now = datetime.datetime.now()
        feed_count = 0
        for feed in feeds:
            feed = pq(feed)
            question_content = _replace_html_tag(feed(".m_feed_txt").eq(0).html()).strip()
            answer_content = _replace_html_tag(feed(".m_feed_txt").eq(1).html()).strip()

            question_time = _get_time(feed(".m_feed_from:eq(0) span").html(), pre_time)
            answer_time = _get_time(feed(".m_feed_from:eq(1) span").html(), pre_time)

            # print question_content.encode("utf8")
            # print answer_content.encode("utf8")
            # print question_time, answer_time

            interface.StockFeedBase().create_feed(stock, question_content, answer_content, belong_market=0, create_time=answer_time,
                                                  create_question_time=question_time)
            pre_time = answer_time if answer_time < now else now
            feed_count += 1
        print (u"处理完成，%s, 共%s条" % (stock.name, feed_count)).encode("utf8")
    end_time = time.time()
    print (u"耗时：%s秒" % int(end_time - start_time)).encode("utf8")


if __name__ == '__main__':
    get_shanghai_feed()
