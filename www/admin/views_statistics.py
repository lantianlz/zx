# -*- coding: utf-8 -*-

import json
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page, get_baidu_spider_info
from www.custom_tags.templatetags.custom_filters import str_display

from www.account.interface import UserBase
from www.question.interface import QuestionBase, AnswerBase


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
            'user_des': str_display(user.des, 17),
            'question_count': user.user_count['user_question_count'],
            'answer_count': user.user_count['user_answer_count'],
            'liked_count': user.user_count['user_liked_count'],
            'follower_count': user.user_count['follower_count'],
            'following_count': user.user_count['following_count'],
            'is_recommend': user.is_recommend,
            'is_admin': user.is_admin,
            'is_customer_manager': user.is_customer_manager,
            'last_active': str(user.last_active),
            'state': user.state,
            'ip': user.last_active_ip
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('')
def register_user(request, template_name='admin/statistics_register_user.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def common_statistics(start_date, end_date, objs):
    '''
    通用统计
    '''
    data = {}

    # 数据库数据
    for x in objs:
        date = str(x.create_time)[5:10]
        if not data.has_key(date):
            data[date] = 0
        data[date] += 1

    temp = {}
    next_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # 构建区间日期字典
    while next_date <= end_date:
        temp[str(next_date)[5:10]] = 0
        next_date += datetime.timedelta(days=1)

    # 合并两块数据
    temp.update(data)

    sort_data = [{'date': k, 'value': temp[k]} for k in temp.keys()]
    sort_data.sort(key=lambda x: x['date'])

    return sort_data


@verify_permission('statistics_register_user')
def statistics_register_user(request):
    '''
    注册用户统计
    '''
    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')

    data = common_statistics(
        start_date, end_date,
        UserBase().get_users_by_range_date(start_date + ' 00:00:00', end_date + ' 23:59:59')
    )

    return HttpResponse(
        json.dumps(data),
        mimetype='application/json'
    )


@verify_permission('statistics_questions')
def statistics_questions(request):
    '''
    提问统计
    '''
    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')

    data = common_statistics(
        start_date, end_date,
        QuestionBase().get_questions_by_range_date(start_date + ' 00:00:00', end_date + ' 23:59:59')
    )

    return HttpResponse(
        json.dumps(data),
        mimetype='application/json'
    )


@verify_permission('statistics_answers')
def statistics_answers(request):
    '''
    提问统计
    '''
    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')

    data = common_statistics(
        start_date, end_date,
        AnswerBase().get_answers_by_range_date(start_date + ' 00:00:00', end_date + ' 23:59:59')
    )

    return HttpResponse(
        json.dumps(data),
        mimetype='application/json'
    )


@verify_permission('')
def statistics_spider_access(request, template_name='admin/statistics_spider_access.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('statistics_spider_access')
def statistics_spider_access_logs(request):
    '''
    提问统计
    '''
    lst_all_info, lst_invalid_info, lst_info_group_by_url = get_baidu_spider_info.get_baidu_spider_info()

    logs = []
    invalid_logs = []
    all_logs = []

    num = 0
    for x in lst_info_group_by_url:
        num += 1

        logs.append({
            'num': num,
            'url': x[0],
            'count': x[1]
        })

    num = 0
    for x in lst_invalid_info:
        num += 1

        invalid_logs.append({
            'num': num,
            'ip': x[0],
            'date': x[1],
            'url': x[2],
            'state': x[3]
        })

    num = 0
    for x in lst_all_info:
        num += 1

        all_logs.append({
            'num': num,
            'ip': x[0],
            'date': x[1],
            'url': x[2],
            'state': x[3]
        })

    return HttpResponse(
        json.dumps({'logs': logs, 'invalid_logs': invalid_logs, 'all_logs': all_logs}),
        mimetype='application/json'
    )
