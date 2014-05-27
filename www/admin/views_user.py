# -*- coding: utf-8 -*-

import json
import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission

from www.account.interface import UserBase, UserCountBase


@verify_permission('')
def user(request, template_name='admin/user.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('query_user')
def search(request):
    user_nick = request.POST.get('user_nick')
    page_index = int(request.POST.get('page_index', 1))
    data = []
    users = []
    ub = UserBase()

    if user_nick:
        users = ub.get_user_by_nick(user_nick)
        users = [users] if users else []
    else:
        users = ub.get_all_users()

    page_objs = page.Cpt(users, count=10, page=page_index).info

    # 格式化
    format_users = [ub.format_user_full_info(x.id) for x in page_objs[0]]

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


@verify_permission('query_user')
def get_user_by_id(request):
    user_id = request.REQUEST.get('user_id')
    data = ''

    user = UserBase().get_user_by_id(user_id)
    if user:
        data = {
            'user_id': user.id,
            'user_nick': user.nick
        }

    return HttpResponse(json.dumps(data), mimetype='application/json')
