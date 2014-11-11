# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def main():
    from www.tasks import async_send_email
    from common import utils
    from www.kaihu.models import CustomerManager
    from www.account.interface import UserBase

    count = 0
    for cm in CustomerManager.objects.filter(state=True):
        user = UserBase().get_user_by_id(cm.user_id)
        if "@a.com" in user.email:
            continue
        print user.email

        context = dict(user=user)
        async_send_email(user.email, u'智选双十一活动，一场属于证券客户经理的狂欢', utils.render_email_template('email/ad/11_email.html', context), 'html')
        print count
        count += 1


if __name__ == '__main__':
    main()
