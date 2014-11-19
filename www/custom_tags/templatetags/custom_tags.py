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
def question_type_radio_display(context):
    """
    @note: 问答类型radio方式展现
    """
    from www.question.interface import TopicBase
    aqts = TopicBase().get_all_question_type()

    return render_to_response('question/_question_type_radio_display.html', locals(),
                              context_instance=context).content


@register.simple_tag(takes_context=True)
def question_type_nav_display(context):
    """
    @note: 问题类型导航方式展现
    """
    from www.question.interface import TopicBase
    aqts = TopicBase().get_all_question_type()
    return render_to_response('question/_question_type_nav_display.html', locals(),
                              context_instance=context).content


@register.simple_tag(takes_context=True)
def global_statistic(context):
    """
    @note: 全站统计信息展现
    """
    from www.question.models import Question, Answer
    from www.account.models import User
    from www.stock.models import StockFeed
    from common import cache

    key = 'global_statistic'
    cache_obj = cache.Cache(config=cache.CACHE_STATIC)

    gs = cache_obj.get(key)
    if not gs:
        answer_count = Answer.objects.filter(state=True).count()
        question_count = Question.objects.filter(state=True).count()
        account_count = User.objects.all().count()
        stock_feed_count = StockFeed.objects.all().count()

        now = datetime.datetime.now()
        stock_feed_latest_time = now.strftime('%Y-%m-%d %H:%M:%S')
        sfs = StockFeed.objects.all().order_by("-create_time")[:1]
        if sfs:
            stock_feed_latest_time = sfs[0].create_time

        gs = dict(answer_count=answer_count, question_count=question_count,
                  account_count=account_count, update_time=now.strftime('%Y-%m-%d %H:%M:%S'),
                  stock_feed_count=stock_feed_count, stock_feed_latest_time=stock_feed_latest_time,
                  )
        cache_obj.set(key, gs, time_out=3600 * 2)
    return render_to_response('include/_global_statistic.html', locals(),
                              context_instance=context).content


@register.simple_tag(takes_context=True)
def user_qa_count_info_right_nav_dispaly(context):
    """
    @note: 个人问答相关统计总数信息获取
    """
    from www.account.interface import UserCountBase
    user_count_info = UserCountBase().get_user_count_info(context['request'].user.id)
    user_question_count, user_answer_count, user_liked_count = user_count_info['user_question_count'],\
        user_count_info['user_answer_count'], user_count_info['user_liked_count']

    return render_to_response('question/_user_qa_count_info_right_nav_dispaly.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def global_hot_topics(context):
    """
    @note: 热门话题
    """
    from www.question.interface import TopicBase

    global_hotest_topics = TopicBase().get_all_topics_for_show()[:5]
    return render_to_response('question/_global_hot_topics.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def latest_article(context):
    """
    @note: 最新资讯
    """
    import re
    from common import utils
    from www.kaihu.interface import ArticleBase, CityBase

    city_abbr = utils.get_sub_domain_from_http_host(context['request'].META.get('HTTP_HOST', ''))
    city = CityBase().get_city_by_pinyin_abbr(city_abbr)

    path = context['request'].path
    p = re.compile(u'\/kaihu/article\/?\d*', re.I)
    ps = dict(city_id=city.id)
    if p.findall(path):
        ps.update(dict(order_by="?"))
    articles = ArticleBase().get_articles_by_city_id(**ps)[:10]

    return render_to_response('kaihu/_latest_article.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def random_department(context):
    """
    @note: 随机出现营业部
    """
    from common import utils
    from www.kaihu.interface import DepartmentBase, CityBase

    city_abbr = utils.get_sub_domain_from_http_host(context['request'].META.get('HTTP_HOST', ''))
    city = CityBase().get_city_by_pinyin_abbr(city_abbr)

    departments = DepartmentBase().get_departments_by_random(city.id)[:10]
    return render_to_response('kaihu/_random_department.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def hot_stock(context):
    """
    @note: 热门股票
    """
    from www.stock.interface import StockBase
    stocks = StockBase().get_all_stocks()[:10]

    return render_to_response('stock/_hot_stock.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def my_stock(context):
    """
    @note: 我关注的股票
    """
    from www.stock.interface import StockFollowBase
    stock_follows = StockFollowBase().get_stock_follows_by_user_id(context['request'].user.id)[:10]
    stocks = [sf.stock for sf in stock_follows]

    return render_to_response('stock/_my_stock.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def toutiao_acticle_type_nav_display(context):
    """
    @note: 头条导航
    """
    from www.toutiao.interface import ArticleTypeBase
    article_type = ArticleTypeBase().get_all_valid_article_type()
    return render_to_response('toutiao/_toutiao_article_type_nav_display.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def toutiao_hotest_articles(context):
    """
    @note: 头条最新热榜
    """
    from www.toutiao.interface import ArticleBase
    articles = ArticleBase().get_hotest_articles()[:10]

    return render_to_response('toutiao/_toutiao_hotest_articles.html', locals(), context_instance=context).content


@register.simple_tag(takes_context=True)
def kaihu_ad(context):
    """
    @note: 头条最新热榜
    """
    from common import utils

    city_abbr = utils.get_sub_domain_from_http_host(context['request'].META.get('HTTP_HOST', ''))
    dict_ads = {"mz": ["ad_mz.jpg", "8655809", u"梅州"], }
    default = ["ad_common.jpg", "403897485", u"通用"]
    ad_img = dict_ads.get(city_abbr, default)

    return render_to_response('kaihu/_kaihu_ad.html', locals(), context_instance=context).content
