# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = 'f762a6f5d2b711e39a09685b35d0bf16'


def main():
    from www.question import interface
    from www.account.interface import UserBase

    user = UserBase().get_user_by_id(user_id)

    lb = interface.LikeBase()
    ab = interface.AnswerBase()
    qb = interface.QuestionBase()

    # lb.like_it(7, from_user_id=user_id, ip='127.0.0.1')
    # ab.remove_answer(41, user)
    # print ab.get_answer_summary_by_id(1)

    print qb.set_important(8, user, img='http://img0.zhixuan.com/important_28.jpg', img_alt='精选描述', sort_num=2)
    # print qb.cancel_important(8, user)


if __name__ == '__main__':
    main()
