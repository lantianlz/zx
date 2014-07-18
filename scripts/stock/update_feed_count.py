# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from www.stock.models import Stock, StockFeed


def update_feed_count():
    for stock in Stock.objects.all():
        stock.feed_count = StockFeed.objects.filter(stock=stock, state=True).count()
        stock.save()

    print 'ok'


if __name__ == '__main__':
    update_feed_count()
