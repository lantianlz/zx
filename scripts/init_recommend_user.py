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
    from www.account.models import RecommendUser, User, Profile
    nicks = [
        u'李小侃', u'深耕A股', u'贪睡的An', u'关灯吃面', u'嘎嘎',
        u'小路', u'星辰大海', u'胡萝卜分你一半', u'快乐的光头阳线', u'起起伏伏的诱惑',
        u'闪闪发亮的女神经', u'citicbanker'
    ]

    for nick in nicks:
        try:
            user = Profile.objects.get(nick=nick)
            RecommendUser.objects.create(user_id=user.id)
        except Profile.DoesNotExist:
            print (u'%s does not exist' % nick).encode('utf8')
    # user_ids = [u.id for u in User.objects.all()[:50]]
    # for user_id in user_ids:
    #     try:
    #         RecommendUser.objects.create(user_id=user_id)
    #     except:
    #         pass

    print 'ok'


if __name__ == '__main__':
    init_recommend_user()
