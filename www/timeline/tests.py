# -*- coding: utf-8 -*-
import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import datetime
from common import utils


from www.timeline import interface
ufb = interface.UserFollowBase()
from_user_id = '83baf86160e611e3b491f319607cbb35'
to_user_id = '28031a9ea94011e3b11afbe1af786b34'


def test():
    print ufb.follow_people(from_user_id, to_user_id, )
    # print ufb.unfollow_people(from_user_id, to_user_id)


if __name__ == '__main__':
    test()
