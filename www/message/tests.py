# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = user = '0dda67e6d98811e3ab90685b35d0bf16'


def main():
    from www.message import interface

    to_user_id = 'f762a6f5d2b711e39a09685b35d0bf16'
    user_id2 = 'f40527cfd2c611e3b50a685b35d0bf16'

    ucb = interface.UnreadCountBase()
    iab = interface.InviteAnswerBase()
    # print ucb.init_count_info()
    # print ucb.get_unread_type()
    # print ucb.get_unread_count_info(user)
    # print ucb.get_unread_count_total(user)
    # print ucb.update_unread_count(user, code='at_answer', operate="add")
    # print ucb.update_unread_count(user, code='system_message', operate="add")
    # print ucb.update_unread_count(user, code='received_like', operate="add")
    # print ucb.update_unread_count(user, code='received_answer', operate="add")

    print iab.update_invite_is_read(to_user_id)
    # print iab.create_invite(from_user_id=user_id2, to_user_id=to_user_id, question_id=8)

if __name__ == '__main__':
    main()
