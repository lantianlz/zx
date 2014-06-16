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
    from www.question.interface import TopicBase
    from www.question.models import Question, QuestionType, Tag, TagQuestion, Topic, TopicQuestion
    tb = TopicBase()

    if not Topic.objects.filter(domain='root'):
        root = Topic.objects.create(name=u"全部", domain="root", des="根话题", level=0)

    for qt in QuestionType.objects.all():
        if not Topic.objects.filter(domain=qt.domain):
            Topic.objects.create(name=qt.name, domain=qt.domain, parent_topic=root, level=tb.get_topic_level_by_parent(root))

    for tag in Tag.objects.select_related('question_type').all():
        if not Topic.objects.filter(domain=tag.domain):
            parent_topic = Topic.objects.get(domain=tag.question_type.domain)
            state = 2 if tag.domain in ('gpzh', 'qhzh', 'lczx') else 1
            Topic.objects.create(name=tag.name, domain=tag.domain, parent_topic=parent_topic, state=state,
                                 img=tag.img, des=tag.des, sort_num=tag.sort_num, level=tb.get_topic_level_by_parent(parent_topic))

    # 重新建立提问的对应关系
    for question in Question.objects.all():
        tags = [tq.tag for tq in TagQuestion.objects.select_related('tag').filter(question=question)]
        topic_ids = [topic.id for topic in [tb.get_topic_by_id_or_domain(tag.domain) for tag in tags]]
        tb.create_topic_question_relation(question, topic_ids)

    # 更新话题的子话题数
    # 更新话题的提问数量
    for topic in Topic.objects.all():
        topic.question_count = TopicQuestion.objects.select_related('question').filter(topic=topic, question__state=True).count()
        topic.child_count = Topic.objects.filter(parent_topic=topic).count()
        topic.save()

    tb.get_all_topics(must_update_cache=True)

    print 'ok'


if __name__ == '__main__':
    init_question_type()
