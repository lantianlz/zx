# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import re
from www.kaihu.models import Department


def update_department_name():
    i = 0
    j = 0
    for department in Department.objects.all():

        # 修复有空格的
        if department.name.strip() != department.name:
            department.name = department.name.strip()
            department.save()
            j += 1

        # 修复有两个证券关键词的
        if department.name.find(u'证券证券') != -1:
            department.name = department.name.replace(u'证券证券', u'证券')
            department.save()
            j += 1

        # 修复公司名重复的
        cname = department.company.name
        if (u'%s%s' % (cname, cname)) in department.name:
            department.name = department.name.replace((u'%s%s' % (cname, cname)), cname)
            department.save()
            i += 1

        # 修复公司名重复并且两个名字不一致的
        p = re.compile(u'(.+?公司)(.+?公司)(.+?[^公司]+?$)', re.DOTALL | re.IGNORECASE)
        names = p.findall(department.name)
        if names:
            print department.company.name.encode('utf8')
            print names[0][2].encode('utf8')

            department.name = u'%s%s' % (department.company.name, names[0][2])
            department.save()
            i += 1

    print 'totoal count is %s' % i
    print 'total need change name count is %s' % j

    print 'ok'

    # p = re.compile(u'(.+?公司)(.+?公司)(.+?[^公司]+?$)', re.DOTALL | re.IGNORECASE)
    # name = u'东北证券股份有限公司东北证券股份有限公司上海南奉公路证券营业部'
    # names = p.findall(name)
    # for n in names[0]:
    #     print n.encode('utf8')
    # print names


if __name__ == '__main__':
    update_department_name()
