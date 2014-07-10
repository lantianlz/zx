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
import re
from pyquery import PyQuery as pq


def is_in_baidu(key):
    print key.encode('utf8')
    for page in range(0, 1):
        url = u"http://www.baidu.com/s?wd=" + key + "&pn=" + \
            str(page) + u"&oq=" + key + "&tn=63090008_1_hao_pg&ie=utf-8&usm=2"
        rep = requests.get(url)
        text = rep.text

        jq = pq(text)
        try:
            text = jq('#content_left').html()
            if key in text:
                return True
        except:
            pass
    return False


def auto_publish_article(key):
    from common.utils import get_summary_from_html_by_sub

    # text = open((u"./txt/%s.txt" % u"【原创】《大雄股市历险记4》股票为什么会上涨").encode("utf8"), "r").read()
    # text = get_summary_from_html_by_sub(text, max_num=990000)
    # print text
    # return
    count = 0
    hrefs = u""

    for index in range(20):
        url = 'http://weixin.sogou.com/weixin?query=' + key + '&type=2&ie=utf8&page=' + str(index) + '&p=40040100&dp=1&w=01019900&dr=1'
        rep = requests.get(url)
        text = rep.text
        jq = pq(text)
        lst_articles = jq('.wx-rb3 .txt-box a')
        for article in lst_articles:
            print count
            href = article.get("href")
            name = article.text_content()
            text = requests.get(href).text
            text = get_summary_from_html_by_sub(text, max_num=990000, filter_nbsp=True)

            re_blank = re.compile('[\s]+', re.I)
            key_text = re_blank.sub('', text)
            if not 300 < len(key_text) < 3000:
                continue
            if is_in_baidu(key_text[50:60]):
                continue
            if is_in_baidu(key_text[150:160]):
                continue
            if is_in_baidu(key_text[250:260]):
                continue
            count += 1
            hrefs += u"%s\n" % href
            open((u"./txt/%s.txt" % name).encode("utf8"), "w").write(text.encode("utf8"))
            # break
        open((u"./txt/hrefs.txt").encode("utf8"), "w").write(hrefs.encode("utf8"))

    print u"total articles:%s" % count


if __name__ == '__main__':
    key = u'原创 股票'
    auto_publish_article(key)
