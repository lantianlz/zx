# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def init_question_tag():
    from www.question.models import QuestionType, Tag
    # Tag.objects.all().delete()
    datas = [
        (u'股票', [
            [u'大盘走势', u'dpzs', True, u'http://img0.zhixuan.com/topic_dpzs.jpg', u''],
            [u'个股分析', u'ggfx', True, u'http://img0.zhixuan.com/topic_ggfx.jpg', u''],
            [u'行业分析', u'hyfx', True, u'http://img0.zhixuan.com/topic_hyfx.jpg', u''],
            [u'宏观经济', u'hgjj', True, u'http://img0.zhixuan.com/topic_hgjj.jpg', u''],
            [u'投资策略', u'tzcl', True, u'http://img0.zhixuan.com/topic_tzcl.jpg', u''],
            [u'海南股', u'hng', False, u'http://img0.zhixuan.com/topic_hng.jpg', u''],
            [u'博彩概念股', u'bcgng', False, u'http://img0.zhixuan.com/topic_bcgng.jpg', u''],
        ]),
        (u'债券', [
            [u'债券分析', u'zqfx', True, u'http://img0.zhixuan.com/topic_zqfx.jpg', u''],
            [u'正回购', u'zhg', True, u'http://img0.zhixuan.com/topic_zhg.jpg', u''],
            [u'可转债', u'kzz', True, u'http://img0.zhixuan.com/topic_kzz.jpg', u''],
        ]),
        (u'期货', [
            [u'商品期货', u'spqh', True, u'http://img0.zhixuan.com/topic_spqh.jpg', u''],
            [u'股指期货', u'gzqh', True, u'http://img0.zhixuan.com/topic_gzqh.jpg', u''],
            [u'国债期货', u'guozqh', True, u'http://img0.zhixuan.com/topic_guozqh.jpg', u''],
        ]),
        (u'期权', [
            [u'个股期权', u'ggqq', True, u'http://img0.zhixuan.com/topic_ggqq.jpg', u''],
        ]),
    ]
    for data in datas:
        qt = QuestionType.objects.get(name=data[0])
        for tag in data[1]:
            try:
                tag_obj = Tag.objects.get(name=tag[0])
                tag_obj.img = tag[3]
                tag_obj.des = tag[4]
                tag_obj.domain = tag[1]
                tag_obj.save()
            except Tag.DoesNotExist:
                Tag.objects.create(name=tag[0], domain=tag[1], question_type=qt, is_show=tag[2])
    print 'ok'


if __name__ == '__main__':
    init_question_tag()
