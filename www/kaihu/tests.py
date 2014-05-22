# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = user = 'f762a6f5d2b711e39a09685b35d0bf16'


def main():
    from www.kaihu import interface
    cmb = interface.CustomerManagerBase()
    print cmb.add_customer_manager(user_id, 2082, end_date='2014-06-01')


if __name__ == '__main__':
    main()
