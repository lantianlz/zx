# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from www.kaihu.models import Department, CustomerManager


def update_department_cm_count():
    department_ids = [cm.department_id for cm in CustomerManager.objects.all()]
    department_ids = list(set(department_ids))
    for department_id in department_ids:
        department = Department.objects.get(id=department_id)
        department.cm_count = CustomerManager.objects.filter(department=department, state=True).count()
        department.save()

    print 'ok'


if __name__ == '__main__':
    update_department_cm_count()
