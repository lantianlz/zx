# -*- coding: utf-8 -*-

import json
import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required

from www.account.interface import RecommendUserBase


def recommend_user(request, template_name='admin/recommend_user.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@staff_required
def get_all_recommend_users(request):
    '''
    获取所有推荐用户
    '''
    recommend_users = RecommendUserBase().get_all_recommend_users()

    result = [{
        'user_id': x.id,
        'user_avatar': x.user.get_avatar_25(),
        'user_nick': x.user.nick,
        'user_des': x.user.des,
        'question_count': x.user_count['user_question_count'],
        'answer_count': x.user_count['user_answer_count'],
        'liked_count': x.user_count['user_liked_count'],
        'follower_count': x.user_count['follower_count'],
        'following_count': x.user_count['following_count'],
        'sort': x.sort_num
    } for x in recommend_users]

    return HttpResponse(json.dumps(result), mimetype='application/json')


@staff_required
def set_recommend_user_sort(request):
    '''
    设置推荐用户排序
    '''
    user_id = request.POST.get('user_id')
    sort_num = request.POST.get('sort_num', 0)

    err_code, msg = RecommendUserBase().set_recommend_user_sort(user_id, sort_num)
    return HttpResponse(json.dumps(err_code), mimetype='application/json')
