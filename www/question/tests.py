# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = '83baf86160e611e3b491f319607cbb35'


def main():
    from www.question import interface
    from www.account.interface import UserBase

    user = UserBase().get_user_by_id(user_id)

    lb = interface.LikeBase()
    ab = interface.AnswerBase()

    # flag, result = lb.like_it(7, from_user_id=user_id, ip='127.0.0.1')
    flag, result = ab.remove_answer(41, user)

    print result.encode('utf8').__repr__()
    print result.encode('utf8')


if __name__ == '__main__':
    # main()

    from common import utils
    import random
    # print random.randint(0, 2)
    print utils.get_random_code()
