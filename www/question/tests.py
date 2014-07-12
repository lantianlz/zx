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
    tb = interface.TopicBase()

    # lb.like_it(7, from_user_id=user_id, ip='127.0.0.1')
    # ab.remove_answer(41, user)
    # print ab.get_answer_summary_by_id(1)

    # print qb.set_important(8, user, title="2014年新规新股申购:9问9答！（号称市场最全面2014.6.1", summary="fasdfadsfadsfads", author_user_id='',
    #                        img='http://img0.zhixuan.com/important_28.jpg', img_alt='这是一个神奇的精选', sort_num=4)
    # print qb.cancel_important(8, user)

    des = """12121"""
    # print tb.create_topic(name=u"测试话题", domain="dpzs1", parent_topic_id=1, des=des, img="", state=1)
    # print tb.modify_topic(topic_id=26, name=u"测试话题", domain="csht", parent_topic_id=2, des=u'测试话题', img="", state=1)

    print UserBase().search_users(u"简单")
    print qb.search_questions("a")


if __name__ == '__main__':
    main()
