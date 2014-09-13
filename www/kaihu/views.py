# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page, utils
from www.timeline.interface import FeedBase
from www.kaihu import interface

cb = interface.CityBase()
db = interface.DepartmentBase()
cmb = interface.CustomerManagerBase()
flb = interface.FriendlyLinkBase()
atb = interface.ArticleBase()
nb = interface.NewsBase()


def home(request, template_name='kaihu/home.html'):
    areas = cb.get_all_areas()
    citys_by_area = cb.get_all_city_group_by_province()
    flinks = flb.get_friendly_link_by_link_type(link_type=1)

    newses = nb.get_all_newses()[:10]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def department_list(request, city_abbr, template_name='kaihu/department_list.html'):
    city = cb.get_city_by_pinyin_abbr(city_abbr)
    if not city:
        raise Http404
    departments = db.get_departments_by_city_id(city.id)
    departments_count = len(departments)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(departments, count=10, page=page_num).info
    departments = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    customer_managers = cmb.get_customer_managers_by_city_id(city.id)
    customer_manager_user_ids = [cm['user_id'] for cm in customer_managers]
    customer_managers = customer_managers[:4]

    if not request.REQUEST.has_key('page'):
        flinks = flb.get_friendly_link_by_city_id(city.id)

    # 获取城市对应区域
    districts = cb.get_districts_by_city(city.id)

    # fb = FeedBase()
    # feeds = fb.format_feeds_by_id(fb.get_feed_ids_by_feed_type(feed_type=3, user_ids=customer_manager_user_ids)[:5])

    city_name_for_seo = city.get_city_name_for_seo()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def department_list_by_district(request, district_id, template_name='kaihu/department_list.html'):
    district = cb.get_district_by_id(district_id)
    if not district:
        raise Http404
    city = cb.get_city_by_id(district.city)

    departments = db.get_departments_by_district_id(district_id)
    departments_count = len(departments)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(departments, count=10, page=page_num).info
    departments = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    customer_managers = cmb.get_customer_managers_by_city_id(city.id)
    customer_manager_user_ids = [cm['user_id'] for cm in customer_managers]
    customer_managers = customer_managers[:4]

    # 获取城市对应区域
    districts = cb.get_districts_by_city(city.id)

    city_name_for_seo = district.get_city_name_for_seo()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def department_detail(request, department_id, template_name='kaihu/department_detail.html'):
    department = db.get_department_by_id(department_id)
    if not department:
        raise Http404

    customer_managers = cmb.format_customer_managers_for_ajax(cmb.get_customer_managers_by_department(department))

    customer_manager_user_ids = [cm['user_id'] for cm in customer_managers]
    fb = FeedBase()
    feeds = fb.format_feeds_by_id(fb.get_feed_ids_by_feed_type(feed_type=3, user_ids=customer_manager_user_ids)[:20])
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def article_list(request, template_name='kaihu/article_list.html'):
    sub_domain = utils.get_sub_domain_from_http_host(request.META.get('HTTP_HOST', ''))
    city = cb.get_city_by_pinyin_abbr(sub_domain)
    if not city:
        raise Http404

    articles = atb.get_articles_by_city_id(city.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(articles, count=20, page=page_num).info
    articles = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def article_detail(request, article_id, template_name='kaihu/article_detail.html'):
    article = atb.get_article_by_id(article_id)
    if not article:
        raise Http404

    city = cb.get_city_by_id(article.city_id)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def news_list(request, template_name='kaihu/news_list.html'):
    newses = nb.get_all_newses()
    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(newses, count=20, page=page_num).info
    newses = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def news_detail(request, news_id, template_name='kaihu/news_detail.html'):
    news = nb.get_news_by_id(news_id)
    if not news:
        raise Http404

    news_next = nb.get_next_news(news)
    news_pre = nb.get_pre_news(news)
    newses_related = nb.get_related_newses(news)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
# ===================================================ajax部分=================================================================#


def get_customer_manager(request):
    '''
    @note: 获取更多的推荐客户经理
    '''
    city_id = request.REQUEST.get('city_id', '')
    page_num = int(request.REQUEST.get('page', 1))
    page_count = 4

    customer_managers = cmb.get_customer_managers_by_city_id(city_id)[(page_num - 1) * page_count:page_num * page_count]

    return HttpResponse(json.dumps(customer_managers), mimetype='application/json')
