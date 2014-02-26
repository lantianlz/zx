# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def init_unread_type():
    from www.message.models import UnreadType

    datas = (
        ('system_message', '条', '系统消息', '/message', '', 0),
        ('received_like', '条', '收到的赞', '/message/received_like', '', 0),
        ('received_answer', '条', '收到的回答', '/question/received_answer', '', 0),
        ('at_answer', '条', '@我的回答', '/question/at_answer', '', 0),
    )

    for data in datas:
        UnreadType.objects.create(code=data[0], measure=data[1], name=data[2], url=data[3], href_name=data[4], type=data[5])
    print 'ok'


if __name__ == '__main__':
    init_unread_type()
