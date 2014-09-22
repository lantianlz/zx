# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from www.kaihu.models import City
from common.utils import get_baidu_rank


def sync_kaihu_city_baidu_rank():
    for city in City.objects.filter(is_show=True, location_type=2):
        baidu_rank = get_baidu_rank(key=u"%s股票开户" % city.get_city_name_for_seo())
        if str(baidu_rank) != str(city.baidu_rank):
            city.baidu_rank = baidu_rank
            city.save()


if __name__ == '__main__':
    sync_kaihu_city_baidu_rank()
