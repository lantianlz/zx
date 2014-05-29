# -*- coding: utf-8 -*-

import json
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import CityBase, DepartmentBase, CustomerManagerBase, FriendlyLinkBase
from www.account.interface import UserBase


@verify_permission('')
def active_user(request, template_name='admin/statistics_active_user.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('statistics_active_user')
def get_active_user(request):
    page_index = int(request.REQUEST.get('page_index', 1))

    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)

    ub = UserBase()
    objs = ub.get_active_users(today)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化
    format_users = [ub.format_user_full_info(x.user_id) for x in page_objs[0]]

    data = []
    num = 10 * (page_index - 1) + 0

    for user in format_users:

        num += 1
        data.append({
            'num': num,
            'user_id': user.id,
            'user_avatar': user.get_avatar_25(),
            'user_nick': user.nick,
            'user_des': user.des,
            'question_count': user.user_count['user_question_count'],
            'answer_count': user.user_count['user_answer_count'],
            'liked_count': user.user_count['user_liked_count'],
            'follower_count': user.user_count['follower_count'],
            'following_count': user.user_count['following_count'],
            'is_recommend': user.is_recommend,
            'is_admin': user.is_admin,
            'is_customer_manager': user.is_customer_manager,
            'last_active': str(user.last_active),
            'state': user.state
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('')
def register_user(request, template_name='admin/statistics_register_user.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
