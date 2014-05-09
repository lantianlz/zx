# -*- coding: utf-8 -*-
import sys
import os
from pprint import pprint

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
fb = interface.FeedBase()
user_id = from_user_id = 'f762a6f5d2b711e39a09685b35d0bf16'
to_user_id = 'df184345d2c611e392ac685b35d0bf16'


def test():
    # print ufb.follow_people(from_user_id, to_user_id, )
    # print ufb.unfollow_people(from_user_id, to_user_id)

    # print fb.get_user_timeline_feed_ids(user_id)
    # print fb.create_feed(to_user_id, feed_type=0, obj_id=3)
    pprint(fb.get_user_timeline(user_id, page_count=5, last_feed_id=5))


if __name__ == '__main__':
    test()
