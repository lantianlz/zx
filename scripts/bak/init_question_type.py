# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def init_question_type():
    from www.question.models import QuestionType
    # QuestionType.objects.all().delete()
    datas = [(1, u'股票', 'gupiao'), (2, u'债券', 'zhaiquan'), (3, u'期货', 'qihuo'),
             (4, u'期权', 'qiquan'), (5, u'其他', 'qita'), ]
    for data in datas:
        QuestionType.objects.create(name=data[1], value=data[0], domain=data[2])
    print 'ok'


if __name__ == '__main__':
    init_question_type()
