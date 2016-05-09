# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page
from www.toutiao import interface

ab = interface.ArticleBase()
atb = interface.ArticleTypeBase()
wmb = interface.WeixinMpBase()


def toutiao_list(request, article_type=None, template_name='toutiao/toutiao_list.html'):
    if not article_type:
        articles = ab.get_all_valid_articles()
    else:
        article_type = atb.get_type_by_domain(article_type)
        if not article_type:
            raise Http404
        articles = ab.get_articles_by_type(article_type)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(articles, count=10, page=page_num).info
    articles = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def weixin_mp_artilce_list(request, weixin_mp_id, template_name='toutiao/toutiao_list.html'):
    weixin_mp = wmb.get_weixin_mp_by_id(weixin_mp_id)
    if not weixin_mp:
        raise Http404
    articles = ab.get_articles_by_weixin_mp(weixin_mp)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(articles, count=10, page=page_num).info
    articles = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def toutiao_detail(request, article_id, template_name='toutiao/toutiao_detail.html'):
    article = ab.get_article_by_id(article_id)
    if not article:
        raise Http404
    article = ab.format_articles([article, ])[0]
    newsest_articles = ab.get_newsest_articles_related(article)[:5]

    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    if not("baidu" in user_agent or "spider" in user_agent):
        ab.add_article_view_count(article_id)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def get_mps(request):
    from toutiao.models import WeixinMp
    import json

    data = []
    for mp in WeixinMp.objects.select_related('article_type').filter(state=True, article_type_id__in=(1,2,3,5)):
        data.append({
            'open_id': mp.open_id,
            'mp_id': mp.id,
            'name': mp.name,
            'ext_id': mp.ext_id
        })

    return HttpResponse(json.dumps(data))


def check_ban_key(title, ban_keys):
    for bk in ban_keys:
        if bk.key in title:
            return False
    return True

def sync_toutiao(request):
    import json, traceback
    from common import debug
    from toutiao.models import WeixinMp, Article, BanKey
    
    mp_id = request.REQUEST.get('mp_id')
    title = request.REQUEST.get('title')
    content = request.REQUEST.get('content')
    url = request.REQUEST.get('url')
    img = request.REQUEST.get('img')
    create_time = request.REQUEST.get('create_time')

    # print url
    # print img
    # printlst_article title.encode("utf8")
    # print content.encode("utf8")
    # print create_time

    try:
        mp = wmb.get_weixin_mp_by_id(mp_id)

        ban_keys = list(BanKey.objects.all())

        if mp.is_silence == False and check_ban_key(title, ban_keys) == False:
            return HttpResponse(json.dumps({'code': 1}))

        if not (Article.objects.filter(from_url=url) or Article.objects.filter(title=title)):
            Article.objects.create(
                title = title, 
                content = content, 
                weixin_mp = mp, 
                from_url = url, 
                img = img,
                create_time = create_time, 
                is_silence = mp.is_silence, 
                article_type = mp.article_type
            )
            return HttpResponse(json.dumps({'code': 0}))
        else:
            return HttpResponse(json.dumps({'code': 2}))
    except Exception, e:
        debug.get_debug_detail(e)
        return HttpResponse(json.dumps({'code': 99}))


def get_img(request):
    import cStringIO, requests

    url = request.REQUEST.get('url')
    try:
        res = requests.get(url)
        buf = cStringIO.StringIO(res.content)
        
        return HttpResponse(buf.getvalue(),'image/gif')
    except Exception, e:
        return Http404

