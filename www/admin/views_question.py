# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import staff_required, common_ajax_response, verify_permission
from common import utils, page

from www.question.interface import QuestionBase


@verify_permission('')
def question(request, template_name='admin/question.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('query_question')
def search(request):
    '''
    分页查询提问，可以根据标题过滤
    '''
    title = request.REQUEST.get('title')
    page_index = int(request.REQUEST.get('page_index', 1))
    order = request.REQUEST.get('order', 'create_time')

    if title:
        questions = QuestionBase().get_question_by_title(title)
    else:
        questions = QuestionBase().get_all_questions_by_order_count(order)

    page_objs = page.Cpt(questions, count=10, page=page_index).info

    data = []
    num = 10 * (page_index - 1) + 0

    for question in page_objs[0]:
        num += 1
        data.append({
            'num': num,
            'question_id': question.id,
            'user_id': question.user.id,
            'user_nick': question.user.nick,
            'title': question.title,
            'description': question.get_summary(),
            'view_count': question.views_count,
            'answer_count': question.answer_count,
            'is_important': question.is_important,
            'is_hide_user': question.is_hide_user,
            'state': question.state,
            'created_time': str(question.create_time)
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_question')
def get_question_by_id(request):
    '''
    根据提问id查询提问信息
    '''
    question_id = request.REQUEST.get('question_id')

    data = ''
    question = QuestionBase().get_question_by_id(question_id)
    if question:
        data = {
            'question_id': question.id,
            'question_title': question.title,
            'question_desc': question.content
        }
    return HttpResponse(json.dumps(data), mimetype='application/json')
