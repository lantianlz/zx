# -*- coding: utf-8 -*-

import json
import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.misc import qiniu_client
from www.misc.decorators import staff_required, common_ajax_response, verify_permission

from www.question.interface import TopicBase


@verify_permission('')
def topic(request, template_name='admin/topic.html'):
    from www.question.models import Topic
    states = [{'name': x[1], 'value': x[0]} for x in Topic.state_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_topic(objs, num):
    data = []

    for x in objs:
        num += 1
        data.append({
            'num': num,
            'topic_id': x.id,
            'name': x.name,
            'domain': x.domain,
            'parent_id': x.parent_topic.id if x.parent_topic else '',
            'parent_name': x.parent_topic.name if x.parent_topic else '',
            'child_count': x.child_count,
            'follower_count': x.follower_count,
            'question_count': x.question_count,
            'level': x.level,
            'img': x.get_img(),
            'des': x.des,
            'sort': x.sort_num,
            'is_show': x.is_show,
            'state': x.state,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('')
def search(request):
    topic_name = request.POST.get('topic_name')
    page_index = int(request.POST.get('page_index', 1))

    data = []

    page_objs = page.Cpt(TopicBase().get_all_topics(), count=10, page=page_index).info

    num = 10 * (page_index - 1)
    data = format_topic(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('')
def get_topics_by_name(request):
    topic_name = request.REQUEST.get('topic_name')

    result = []

    topics = TopicBase().get_topics_by_name(topic_name)

    if topics:
        for x in topics:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')


@verify_permission('')
def get_topic_by_id(request):
    data = ""

    topic_id = request.REQUEST.get('topic_id')

    obj = TopicBase().get_topic_by_id_or_domain(topic_id)

    if obj:
        data = format_topic([obj], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('')
def modify_topic(request):
    topic_id = request.REQUEST.get('topic_id')
    name = request.REQUEST.get('name')
    domain = request.REQUEST.get('domain')
    des = request.REQUEST.get('des')
    state = request.REQUEST.get('state')
    sort = request.REQUEST.get('sort')
    parent_topic_id = request.REQUEST.get('parent_id')

    tb = TopicBase()
    obj = tb.get_topic_by_id_or_domain(topic_id)
    img_name = obj.img

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='topic')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, code = tb.modify_topic(topic_id, name, domain, img_name, des, state, parent_topic_id)
    print flag, code, '********************'
    url = "/admin/topic#modify/%s" % topic_id

    return HttpResponseRedirect(url)
