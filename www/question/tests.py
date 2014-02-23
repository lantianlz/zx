# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = '83baf86160e611e3b491f319607cbb35'

def main():
    from www.question import interface

    lb = interface.LikeBase()
    flag, result = lb.like_it(7, from_user_id=user_id, ip='127.0.0.1')
    print result.encode('utf8')


if __name__ == '__main__':
	main()