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

    def _get_time(origin_time):
        now = datetime.datetime.now()
        pre_year = int(now.strftime("%Y"))

        if u"昨天" in origin_time:
            now = datetime.datetime.now()
            now_month = int(now.strftime("%m"))
            now_day = int(now.strftime("%d"))
            origin_time = origin_time.strip().replace(u"昨天", (u"%s月%s日" % (now_month, now_day - 1)))
        if u"月" in origin_time:
            result_time = datetime.datetime.strptime((u"%s年%s" % (pre_year, origin_time)).encode("utf8"), '%Y年%m月%d日 %H:%M')
            return result_time
        if u"分钟" in origin_time:
            minute = int(origin_time.split(u"分钟")[0])
            return now - datetime.timedelta(minutes=minute)
        if u"小时" in origin_time:
            hour = int(origin_time.split(u"小时")[0])
            return now - datetime.timedelta(hours=hour)
        if u"秒" in origin_time:
            return now

        raise Exception, (u"time error:%s" % origin_time).encode("utf8")

    start_time = time.time()
    exist_count = 0
    updated_exist_count = 0
    new_count = 0
    for i in range(1, 10):
        url = "http://sns.sseinfo.com/ajax/feeds.do?type=11&pageSize=100&lastid=-1&show=-1&page=%s" % i
        resp = requests.get(url, timeout=30)
        text = resp.text
        # print text.encode("utf8")

        jq = pq(text)
        feeds = jq('.m_feed_item')
        feed_count = 0
        break_flag = False
        for feed in feeds:
            feed = pq(feed)
            question_content = _replace_html_tag(feed(".m_feed_txt").eq(0).html()).strip()
            answer_content = _replace_html_tag(feed(".m_feed_txt").eq(1).html()).strip()

            question_time = _get_time(feed(".m_feed_from:eq(0) span").html())
            answer_time = _get_time(feed(".m_feed_from:eq(1) span").html())

            # print question_content.encode("utf8")
            # print answer_content.encode("utf8")
            # print question_time
            # print answer_time

            re_code = re.compile('\((\d+?)\)')
            code = re_code.findall(question_content)[0]
            stock = interface.StockBase().get_stock_by_code(code, state=None)
            if not stock:
                raise Exception, u"can not find stock:%s" % code

            # 若果已经连续命中200个以上，break，上海动态原始数据存在时间有误的问题，需要剔除
            exist_stock_feeds = list(StockFeed.objects.filter(question_content=question_content, stock=stock))
            if exist_stock_feeds:
                exist_count += 1
                exist_stock_feed = exist_stock_feeds[0]
                if exist_stock_feed.create_time != answer_time:
                    exist_stock_feed.create_time = answer_time
                    exist_stock_feed.create_question_time = question_time
                    exist_stock_feed.save()
                    updated_exist_count += 1
            else:
                new_count += 1
                exist_count = 0
                interface.StockFeedBase().create_feed(stock, question_content, answer_content, belong_market=0, create_time=answer_time,
                                                      create_question_time=question_time)
            if exist_count > 200:
                break_flag = True
                break

            feed_count += 1

        print (u"处理完成第%s轮, 共%s条" % (i, feed_count)).encode("utf8")
        if break_flag:
            break

    end_time = time.time()
    print (u"耗时：%s秒" % int(end_time - start_time)).encode("utf8")
    print (u"共更新了%s条记录的回答时间" % updated_exist_count).encode("utf8")
    print (u"共新增了%s条" % new_count).encode("utf8")


if __name__ == '__main__':
    get_shanghai_feed()
