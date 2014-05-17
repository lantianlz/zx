# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def init_kaihu_info():
    import json
    from pprint import pprint

    data = open('./kaihu/quanshang.txt').read()
    data = json.loads(data)
    departments = data['result']
    pprint(departments[:5])
    print len(departments)

    print 'ok'


if __name__ == '__main__':
    init_kaihu_info()
