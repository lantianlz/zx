# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from www.kaihu.models import Department, City


def update_city_department_count():
    for city in City.objects.all():
        department_count = Department.objects.filter(city_id=city.id).exclude(des=None).count()
        city.department_count = department_count
        city.save()

    print 'ok'


if __name__ == '__main__':
    update_city_department_count()
