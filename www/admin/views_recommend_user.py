# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import staff_required, common_ajax_response, verify_permission
from www.custom_tags.templatetags.custom_filters import str_display
from www.account.interface import RecommendUserBase


@verify_permission('')
def recommend_user(request, template_name='admin/recommend_user.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('query_recommend_user')
def get_all_recommend_users(request):
    '''
    获取所有推荐用户
    '''
    recommend_users = RecommendUserBase().get_all_recommend_users()

    data = []
    num = 0
    for x in recommend_users:
        num += 1

        data.append({
            'user_id': x.user.id,
            'user_avatar': x.user.get_avatar_25(),
            'user_nick': x.user.nick,
            'user_des': str_display(x.user.des, 17),
            'question_count': x.user_count['user_question_count'],
            'answer_count': x.user_count['user_answer_count'],
            'liked_count': x.user_count['user_liked_count'],
            'follower_count': x.user_count['follower_count'],
            'following_count': x.user_count['following_count'],
            'sort_num': x.sort_num,
            'num': num,
            'is_recommend': True
        })

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_recommend_user')
@common_ajax_response
def set_recommend_user_sort(request):
    '''
    设置推荐用户排序
    '''
    user_id = request.POST.get('user_id')
    sort_num = request.POST.get('sort_num', 0)

    return RecommendUserBase().set_recommend_user_sort(user_id, sort_num)


@verify_permission('set_recommend_user')
@common_ajax_response
def set_recommend_user(request):
    '''
    设置推荐用户
    '''
    user_id = request.POST.get('user_id')

    return RecommendUserBase().set_recommend_user(user_id)


@verify_permission('cancel_recommend_user')
@common_ajax_response
def un_recommend_user(request):
    '''
    取消推荐用户
    '''
    user_id = request.POST.get('user_id')

    return RecommendUserBase().un_recommend_user(user_id)


@verify_permission('query_recommend_user')
def get_user_by_nick(request):
    '''
    根据用户呢称查询用户详细信息
    '''
    nick = request.POST.get('nick_name')
    data = []

    user = RecommendUserBase().get_user_by_nick(nick)

    if user:
        data.append({
            'user_id': user.id,
            'user_avatar': user.get_avatar_25(),
            'user_nick': user.nick,
            'user_des': user.des,
            'question_count': user.user_count['user_question_count'],
            'answer_count': user.user_count['user_answer_count'],
            'liked_count': user.user_count['user_liked_count'],
            'follower_count': user.user_count['follower_count'],
            'following_count': user.user_count['following_count'],
            'num': 1,
            'is_recommend': user.is_recommend
        })
    return HttpResponse(json.dumps(data), mimetype='application/json')
