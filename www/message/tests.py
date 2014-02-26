# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = user = '83baf86160e611e3b491f319607cbb35'

def main():
    from www.message import interface

    ucb = interface.UnreadCountBase()
    print ucb.init_count_info()
    print ucb.get_unread_type()
    print ucb.get_unread_count(user)
    print ucb.get_unread_count_total(user)
    # print ucb.update_unread_count(user, code='at_answer')

if __name__ == '__main__':
	main()