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
    import datetime
    from www.tasks import async_send_email_worker
    from common import utils
    from www.account.models import User

    count = 0
    for user in User.objects.filter(state__gt=0):
        if "@a.com" in user.email:
            continue
        print user.email

        print count
        count += 1

        context = dict(now_date=datetime.datetime.now().date(), email=user.email)
        try:
            async_send_email_worker(user.email, u'财经微头条，你获取财经资讯的最佳选择', utils.render_email_template('email/ad/weitoutiao_email.html', context), 'html')
        except Exception, e:
            print e


if __name__ == '__main__':
    main()
