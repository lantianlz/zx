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
from www.kaihu.models import News

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"}


def sync_kaihu_news():
    def _replace_html_tag(text):
        tag_s = re.compile('<.+?>')
        tag_e = re.compile('</\w+?>')
        text = tag_s.sub('', text)
        text = tag_e.sub(' ', text)
        return text

    start_time = time.time()
    all_count = 0
    department_count = 0

    # 文章字数少于300的过滤，每天更新一次
    for i in range(1, 21):
        url = u"http://weixin.sogou.com/weixin?query=证券营业部&type=1&ie=utf8&page=%s" % i
        resp = requests.get(url, headers=headers, timeout=30)
        text = resp.text
        # print text.encode("utf8")

        jq = pq(text)
        news_hrefs = jq('.txt-box>p:eq(2) a')
        news_count = 0
        break_flag = False
        for href in news_hrefs:
            if href is not None:
                href = pq(href).attr("href").strip()
                news = pq(requests.get(href, headers=headers, timeout=30).text)

                department_name = news("#post-user").html().strip()
                title = news("#activity-name").html().split("<em")[0].strip()
                content = news("#js_content").html()
                format_content = _replace_html_tag(content).strip()
                if len(format_content) < 300:
                    continue
                create_time = news("#post-date").html().strip()
                create_time = datetime.datetime.strptime(create_time.encode("utf8"), '%Y-%m-%d')

                # print department_name.encode("utf8")
                # print title.encode("utf8")
                # print format_content.encode("utf8")
                # print create_time

                department_count += 1
                if not (News.objects.filter(from_url=href) or News.objects.filter(title=title)):
                    News.objects.create(title=title, content=content, department_name=department_name, from_url=href, create_time=create_time)
                else:
                    continue

                if all_count > 500:
                    break_flag = True
                    break

                news_count += 1
                all_count += 1
            else:
                print "find a no news department"

        # print (u"处理完成第%s轮, 共%s条" % (i, news_count)).encode("utf8")
        if break_flag:
            break

    end_time = time.time()
    print (u"耗时：%s秒" % int(end_time - start_time)).encode("utf8")
    print (u"共更新%s个营业部" % department_count).encode("utf8")
    print (u"共新增了%s条" % all_count).encode("utf8")


if __name__ == '__main__':
    sync_kaihu_news()
