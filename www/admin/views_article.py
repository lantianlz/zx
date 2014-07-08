# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import ArticleBase, CityBase, DepartmentBase


@verify_permission('')
def article(request, template_name='admin/article.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_article')
@common_ajax_response
def add_article(request):
    title = request.REQUEST.get('title')
    content = request.REQUEST.get('content')
    city_id = request.REQUEST.get('belong_city')
    department_id = request.REQUEST.get('belong_department')
    sort_num = request.REQUEST.get('sort')

    # 如果设置了营业部，则使用营业部所属城市
    if department_id:
        city_id = DepartmentBase().get_department_by_id(department_id).city.id

    code, obj = ArticleBase().add_article(title, content, city_id, department_id, sort_num)

    return code, obj.id


def format_article(objs, num):
    data = []

    for x in objs:
        num += 1
        data.append({
            'num': num,
            'article_id': x.id,
            'title': x.title,
            'content': x.content,
            'city_id': x.city_id if x.city_id else '',
            'city_name': CityBase().get_city_by_id(x.city_id).city if x.city_id else '',
            'department_id': x.department_id if x.department_id else '',
            'department_name': DepartmentBase().get_department_by_id(x.department_id).name if x.department_id else '',
            'sort_num': x.sort_num,
            'state': x.state,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_article')
def search(request):
    data = []
    ab = ArticleBase()

    title = request.REQUEST.get('title')

    objs = []
    if title:
        objs = ab.get_article_by_title(title)
    else:
        objs = ab.get_all_articles(state=None)

    page_index = int(request.REQUEST.get('page_index'))

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_article(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_article')
def get_article_by_id(request):
    article_id = request.REQUEST.get('article_id')

    obj = ArticleBase().get_article_by_id(article_id, need_state=False)

    data = format_article([obj], 1)[0]
    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('remove_article')
@common_ajax_response
def remove_article(request):
    article_id = request.REQUEST.get('article_id')
    return ArticleBase().remove_article(article_id)


@verify_permission('modify_article')
@common_ajax_response
def modify_article(request):

    article_id = request.REQUEST.get('article_id')

    title = request.REQUEST.get('title')
    content = request.REQUEST.get('content')
    city_id = request.REQUEST.get('belong_city')
    department_id = request.REQUEST.get('belong_department')
    sort_num = request.REQUEST.get('sort')

    # 如果设置了营业部，则使用营业部所属城市
    if department_id:
        city_id = DepartmentBase().get_department_by_id(department_id).city.id

    return ArticleBase().modify_article(article_id, title=title, content=content, city_id=city_id, department_id=department_id, sort_num=sort_num)
