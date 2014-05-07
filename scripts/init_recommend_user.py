# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def init_recommend_user():
    from www.account.models import RecommendUser, User
    user_ids = [u.id for u in User.objects.all()[:50]]
    for user_id in user_ids:
        RecommendUser.objects.create(user_id=user_id)

    print 'ok'


if __name__ == '__main__':
    init_recommend_user()
