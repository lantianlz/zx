# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = 'f762a6f5d2b711e39a09685b35d0bf16'


def main():
    from www.zhuanti import interface
    ztb = interface.ZhuantiBase()

    print ztb.create_zhuanti(title=u"炒股入门", summary=u"炒股入门专题，炒股入门必看", img=u"http://img0.zhixuan.com/important_b4d2e1fefe9f11e3914100163e003240",
                             domain=u"cgrm", author_name=u"智选")


if __name__ == '__main__':
    main()
