# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


from common import utils
from www.question.models import Question
from www.account.models import User
from www.tasks import async_send_email


def send_weekly_email():
    context = dict()
    for user in User.objects.filter(state__gt=0):
        email = user.email
        print email

    email = ["lz@zhixuan.com", "lcm@zhixuan.com"]
    async_send_email(email, u'智选每周精选', utils.render_email_template('email/important.html', context), 'html')

    print 'ok'


if __name__ == '__main__':
    send_weekly_email()
