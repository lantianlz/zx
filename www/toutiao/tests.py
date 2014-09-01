# -*- coding: utf-8 -*-
import sys
import os
from pprint import pprint

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import datetime
from common import utils


from www.toutiao import interface
wmp = interface.WeixinMpBase()
atb = interface.ArticleTypeBase()
bb = interface.BanKeyBase()


def test():
    # ts = wmp.get_mp_info_by_open_id("oIWsFtzU9XFaZY7vsx3qkvrDQ86A")
    # print wmp.add_mp(*ts, article_type=1)
    # print atb.add_article_type(name="综合财经", domain="zhcj")
    print bb.add_ban_key(u"耗资")


if __name__ == '__main__':
    test()
