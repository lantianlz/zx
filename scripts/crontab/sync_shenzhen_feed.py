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


def get_shenzhen_feed():
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

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0",
               "Referer": "http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do",
               "Content-Type": "application/x-www-form-urlencoded",
               }

    start_time = time.time()
    exist_count = 0
    updated_exist_count = 0
    new_count = 0
    for page in range(1, 50):
        url = "http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do?pageNo=%s" % page

        for j in range(3):
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                break
            except:
                pass
        text = resp.text
        # print text.encode("utf8")

        jq = pq(text)
        feed_count = 0
        break_flag = False

        feeds = jq('.talkList2>div')
        # print len(feeds)
        for i in range(0, len(feeds)):
            if i % 2 != 0:
                continue
            question_feed = pq(feeds[i])
            answer_feed = pq(feeds[i + 1])

            question_content = _replace_html_tag(question_feed(".cntcolor").html()).strip()
            answer_content = _replace_html_tag(answer_feed(".cntcolor").html()).strip()
            question_time = _get_time(question_feed(".date").html())
            answer_time = _get_time(answer_feed(".date").html())

            href = question_feed(".cntcolor").attr("href")
            origin_id = href.split("questionId=")[1].split("&")[0]

            if question_content.endswith("...") or answer_content.endswith("..."):
                # print "go on"
                url = "http://irm.cninfo.com.cn/ircs/interaction/viewQuestionForSzseSsgs.do?questionId=%s&condition.replyOrderType=1&condition.searchRange=0" % origin_id
                for j in range(3):
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
            # print question_time
            # print answer_time
            # print origin_id

            re_code = re.compile('\((\d+?)\)')
            code_content = question_feed(".blue2").html().strip()
            code = re_code.findall(code_content)[0]
            stock = interface.StockBase().get_stock_by_code(code, state=None)
            # print stock.name.encode("utf8")
            if not stock:
                print u"can not find stock:%s" % code

            # 若果已经连续命中n个以上，break
            exist_stock_feeds = list(StockFeed.objects.filter(origin_id=origin_id, stock=stock))
            if exist_stock_feeds:
                exist_count += 1
                # exist_stock_feed = exist_stock_feeds[0]
                # if exist_stock_feed.create_time != answer_time:
                #     exist_stock_feed.create_time = answer_time
                #     exist_stock_feed.create_question_time = question_time
                #     exist_stock_feed.save()
                #     updated_exist_count += 1
            else:
                new_count += 1
                exist_count = 0
                interface.StockFeedBase().create_feed(stock, question_content, answer_content, belong_market=1, create_time=answer_time,
                                                      create_question_time=question_time, origin_id=origin_id)
            if exist_count > 50:
                break_flag = True
                break

            feed_count += 1

        print (u"处理完成第%s轮, 共%s条" % (page, feed_count)).encode("utf8")
        if break_flag:
            break

    end_time = time.time()
    print (u"耗时：%s秒" % int(end_time - start_time)).encode("utf8")
    print (u"共更新了%s条记录的回答时间" % updated_exist_count).encode("utf8")
    print (u"共新增了%s条" % new_count).encode("utf8")


if __name__ == '__main__':
    get_shenzhen_feed()
