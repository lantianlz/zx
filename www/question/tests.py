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

    # print qb.set_important(8, user, img='http://img0.zhixuan.com/important_28.jpg', img_alt='精选描述', sort_num=4)
    # print qb.cancel_important(8, user)

    des = """
    <p>大盘：是指沪市的“上证综合指数”和深市的“深证成份股指数”的股票。</p>
    <p>上证综指和深证成指是运用统计学中的指数方法编制而成的，反映沪深股市总体价格变动和走势的指标。</p>
    <p>大盘走势可理解为沪深股市走势。</p>
    """
    # print tb.create_topic(name=u"测试话题", domain="dpzs1", parent_topic_id=1, des=des, img="", state=1)
    print tb.modify_topic(topic_id=26, name=u"测试话题", domain="dpzs1", parent_topic_id=1, des=u'测试话题', img="", state=2)


if __name__ == '__main__':
    main()
