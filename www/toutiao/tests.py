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


def test():
    ts = wmp.get_mp_info_by_open_id("oIWsFt9BhOlk3j8cZi8xcqMzc26c")
    # print wmp.add_mp(*ts)
    print atb.add_article_type(name="综合财经", domain="zhcj")


if __name__ == '__main__':
    test()
