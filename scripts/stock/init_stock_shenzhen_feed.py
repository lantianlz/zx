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


def init_stock_shenzhen_feed():
    def _replace_html_tag(text):
        tag_s = re.compile('<[^\/]+?>')
        tag_e = re.compile('</\w+?>')
        tag_nbsp = re.compile('\&[\w\#]+?;', re.I)
        text = tag_s.sub('', text)
        text = tag_e.sub(' ', text)
        text = tag_nbsp.sub('', text)
        return text

    def _get_time(origin_time):
        origin_time = origin_time.replace(u"（", "").replace(u"）", "").strip()
        return datetime.datetime.strptime(origin_time.encode("utf8"), '%Y年%m月%d日 %H:%M')

    start_time = time.time()
    for stock in Stock.objects.filter(belong_market=1).order_by("id"):
        print stock.name.encode("utf8")
        # url = "http://irm.cninfo.com.cn/ircs/interaction/lastRepliesforSzseSsgs.do?condition.type=1&condition.stockcode=%s&condition.stocktype=S" % stock.code
        # for i in range(3):
        #     try:
        #         resp = requests.get(url, timeout=10)
        #         break
        #     except:
        #         pass
        # text = resp.text
        # jq = pq(text)
        # page_total = int(jq(".sabrosus #pageNo_f").prev().prev().prev().html())
        # print (u"总页数:%s" % page_total).encode("utf8")

        page_total = 1
        feed_count = 0
        for i in range(1, page_total + 1):
            url = "http://irm.cninfo.com.cn/ircs/interaction/lastRepliesforSzseSsgs.do?condition.type=1&condition.stockcode=%s&condition.stocktype=S" % stock.code
            data = {"condition.searchType": "code", "pageNo": i, "pageSize": 10, "requestMethod": "GET", "requestUri": "/ircs/interaction/lastRepliesforSzseSsgs.do", "source": "2"}
            for i in range(3):
                try:
                    resp1 = requests.post(url, data=data, timeout=10)
                    break
                except:
                    pass
            text = resp1.text
            # print text.encode("utf8")

            jq = pq(text)

            feeds = jq('.gray')
            for feed in feeds:
                feed = pq(feed)
                question_content = _replace_html_tag(feed(".dtwz_text1:eq(0)>p:eq(1)>a").html()).strip()
                answer_content = _replace_html_tag(feed(".dtwz_text1:eq(1)>p:eq(1)>a").html()).strip()
                question_time = _get_time(feed(".dtwz_text1:eq(0)>p:eq(1)>span").html())
                answer_time = _get_time(feed(".date_box>a").html())

                href = feed(".dtwz_text1:eq(0)>p:eq(1)>a").attr("href")
                origin_id = href.split("questionId=")[1].split("&")[0]

                if question_content.endswith("...") or answer_content.endswith("..."):
                    print "go on"
                    url = "http://irm.cninfo.com.cn/ircs/interaction/viewQuestionForSzseSsgs.do?questionId=%s&condition.replyOrderType=1&condition.searchRange=0" % origin_id
                    for i in range(3):
                        try:
                            text = requests.get(url, timeout=10).text
                            break
                        except:
                            pass
                    jq = pq(text)
                    question_content = _replace_html_tag(jq(".msgBox:eq(0)>div>div").html().split("</a>")[-1]).strip()
                    answer_content = _replace_html_tag(jq(".answerBox:eq(0)>div").html().split("</a>")[-1].split(":", 1)[-1]).strip()

                # print question_content.encode("utf8")
                # print answer_content.encode("utf8")
                # print question_time, answer_time
                # print origin_id

                try:
                    if not StockFeed.objects.filter(origin_id=origin_id):
                        interface.StockFeedBase().create_feed(stock, question_content, answer_content, belong_market=1, create_time=answer_time,
                                                              create_question_time=question_time, origin_id=origin_id)
                    else:
                        break
                except:
                    pass
                feed_count += 1
            break
        # break
        print (u"处理完成，%s, 共%s条" % (stock.name, feed_count)).encode("utf8")
    end_time = time.time()
    print (u"耗时：%s秒" % int(end_time - start_time)).encode("utf8")


if __name__ == '__main__':
    init_stock_shenzhen_feed()
