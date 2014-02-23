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

    datas = [
        (u'大盘', [[u'大一话题', u'dayi'], [u'大二话题', u'daer'], [u'大三话题', u'dasan']]),
        (u'个股', [[u'个一话题', u'geyi'], [u'个二话题', u'geer'], [u'个三话题', u'gesan']]),
    ]
    for data in datas:
        qt = QuestionType.objects.get(name=data[0])
        for tag in data[1]:
        	Tag.objects.create(name=tag[0], domain=tag[1], question_type=qt)
    print 'ok'


if __name__ == '__main__':
    init_question_tag()
