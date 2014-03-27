# -*- coding: utf-8 -*-
"""
@note: 自定义标签文件
@author: lizheng
"""
import datetime
from django import template
register = template.Library()

from django.shortcuts import render_to_response
# from django.template import RequestContext


@register.simple_tag
def current_time(format_string):
    """
    @note: 当前时间tag
    """
    return datetime.datetime.now().strftime(format_string)


@register.simple_tag(takes_context=True)
def import_variable(context, name, value, json_flag=False):
    """
    @note: 传入一个变量到context中
    """
    from django.utils.encoding import smart_str
    import json
    value = smart_str(value)
    context[name] = value if not json_flag else json.loads(value)
    return ''


@register.simple_tag(takes_context=True)
def question_type_option_display(context):
    """
    @note: 问答类型option方式展现
    """
    from www.question.interface import QuestionTypeBase
    aqts = QuestionTypeBase().get_all_question_type()

    return render_to_response('question/_question_type_option_display.html', locals(),
                              context_instance=context).content

@register.simple_tag(takes_context=True)
def question_type_radio_display(context):
    """
    @note: 问答类型radio方式展现
    """
    from www.question.interface import QuestionTypeBase
    aqts = QuestionTypeBase().get_all_question_type()

    return render_to_response('question/_question_type_radio_display.html', locals(),
                              context_instance=context).content


@register.simple_tag(takes_context=True)
def question_type_nav_display(context):
    """
    @note: 问题类型导航方式展现
    """
    from www.question.interface import QuestionTypeBase
    aqts = QuestionTypeBase().get_all_question_type()
    return render_to_response('question/_question_type_nav_display.html', locals(),
                              context_instance=context).content


@register.simple_tag(takes_context=True)
def global_statistic(context):
    """
    @note: 全站统计信息展现
    """
    from www.question.models import Question, Answer
    from www.account.models import User
    from common import cache

    key = 'global_statistic'
    cache_obj = cache.Cache(config=cache.CACHE_STATIC)

    gs = cache_obj.get(key)
    if not gs:
        answer_count = Answer.objects.all().count()
        question_count = Question.objects.all().count()
        account_count = User.objects.all().count()
        now = datetime.datetime.now()
        gs = dict(answer_count=answer_count, question_count=question_count,
                  account_count=account_count, update_time=now.strftime('%Y-%m-%d %H:%M:%S'))
        cache_obj.set(key, gs, time_out=3600 * 8)
    return render_to_response('include/_global_statistic.html', locals(),
                              context_instance=context).content


@register.simple_tag(takes_context=True)
def user_qa_count_info_right_nav_dispaly(context):
    """
    @note: 个人问答相关统计总数信息获取
    """
    from www.question import interface
    user_question_count, user_answer_count, user_liked_count = interface.QuestionBase()\
        .get_user_qa_count_info(context['request'].user.id)
    return render_to_response('question/_user_qa_count_info_right_nav_dispaly.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def global_hotest_tags(context):
    """
    @note: 热门话题提取
    """
    from www.question.interface import TagBase
    global_hotest_tags = TagBase().get_all_tags()
    return render_to_response('question/_global_hotest_tags.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def global_hot_topics(context):
    """
    @note: 热门话题
    """
    #from www.question.interface import TagBase
    #global_hotest_tags = TagBase().get_all_tags()
    return render_to_response('question/_global_hot_topics.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def global_recommend_users(context):
    """
    @note: 推荐用户
    """
    #from www.question.interface import TagBase
    #global_hotest_tags = TagBase().get_all_tags()
    return render_to_response('account/_global_recommend_users.html', locals(), context_instance=context).content
