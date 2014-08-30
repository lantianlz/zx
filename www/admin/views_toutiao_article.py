# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.toutiao.interface import ArticleTypeBase, WeixinMpBase, ArticleBase


@verify_permission('')
def article(request, template_name='admin/toutiao_article.html'):
    types = [{'value': x.id, 'name': x.name} for x in ArticleTypeBase().get_all_valid_article_type()]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_toutiao_article')
@common_ajax_response
def add_article(request):
    title = request.REQUEST.get('title')
    content = request.REQUEST.get('content')
    article_type = request.REQUEST.get('article_type')
    weixin_mp_id = request.REQUEST.get('weixin_id')
    from_url = request.REQUEST.get('from_url', '')
    img = request.REQUEST.get('img')
    is_silence = request.REQUEST.get('is_silence')
    sort_num = request.REQUEST.get('sort_num')

    code, msg = ArticleBase().add_article(title, content, article_type, weixin_mp_id, from_url, img, sort_num, is_silence)

    return code, msg if code else msg.id


def format_article(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'article_id': x.id,
            'title': x.title,
            'content': x.content,
            'article_type': x.article_type.id if x.article_type else '',
            'weixin_id': x.weixin_mp.id,
            'weixin_name': x.weixin_mp.name,
            'from_url': x.from_url,
            'is_silence': x.is_silence,
            'img': x.img,
            'views_count': x.views_count,
            'sort_num': x.sort_num,
            'state': x.state,
            'create_date': str(x.create_time)
        })

    return data


@verify_permission('query_toutiao_article')
def search(request):
    data = []

    title = request.REQUEST.get('title')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False

    page_index = int(request.REQUEST.get('page_index'))

    objs = ArticleBase().search_article_for_admin(title, state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_article(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_toutiao_article')
def get_article_by_id(request):
    article_id = request.REQUEST.get('article_id')

    data = format_article([ArticleBase().get_article_by_id(article_id, None)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_toutiao_article')
@common_ajax_response
def modify_article(request):
    article_id = request.REQUEST.get('article_id')
    title = request.REQUEST.get('title')
    content = request.REQUEST.get('content')
    article_type = request.REQUEST.get('article_type')
    weixin_mp_id = request.REQUEST.get('weixin_id')
    from_url = request.REQUEST.get('from_url', '')
    img = request.REQUEST.get('img')
    is_silence = request.REQUEST.get('is_silence')
    sort_num = request.REQUEST.get('sort_num')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False

    return ArticleBase().modify_article(
        article_id, title=title, content=content, article_type_id=article_type,
        weixin_mp_id=weixin_mp_id, from_url=from_url, img=img, is_silence=is_silence,
        sort_num=sort_num, state=state
    )


@verify_permission('modify_toutiao_article')
@common_ajax_response
def toggle_state(request):
    article_id = request.REQUEST.get('article_id')

    return ArticleBase().toggle_state(article_id)
