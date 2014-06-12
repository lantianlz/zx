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
    from www.question.models import Question, QuestionType, Tag, Topic

    root = Topic.objects.create(name=u"全部", domain="root", des="根话题")

    for qt in QuestionType.objects.all():
        Topic.objects.create(name=qt.name, domain=qt.domain, parent_topic=root)

    for tag in Tag.objects.select_related('question_type').all():
        Topic.objects.create(name=tag.name, domain=tag.domain, parent_topic=Topic.objects.get(domain=tag.question_type.domain),
                             img=tag.img, des=tag.des, sort_num=tag.sort_num)

    # 重新建立提问的对应关系
    for question in Question.objects.filter(state=True):
        pass

    # 更新话题的子话题数
    # 更新话题的提问数量
    for topic in Topic.objects.all():
        pass

    print 'ok'


if __name__ == '__main__':
    init_question_type()
