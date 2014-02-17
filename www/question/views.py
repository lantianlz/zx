# -*- coding: utf-8 -*-

import urllib
import json
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.question import interface
from www.misc.decorators import member_required


@member_required
def question_home(request, question_type=0, template_name='question/question_home.html'):
    qb = interface.QuestionBase()
    questions = qb.get_questions(question_type_domain=question_type)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=3, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def question_detail(request, question_id, template_name='question/question_detail.html',
                    error_msg=None, content=''):
    qb = interface.QuestionBase()
    question = qb.get_question_by_id(question_id)
    question = qb.format_quesitons([question, ])[0]
    if not question:
        raise Http404

    answers = qb.get_answers_by_question_id(question_id)
    answers = qb.format_answers(answers)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def ask_question(request, template_name='question/ask_question.html'):
    if request.POST:
        question_type = int(request.POST.get('question_type', '0'))
        question_title = request.POST.get('question_title')
        question_content = request.POST.get('question_content')
        is_hide_user = request.POST.get('is_hide_user')

        qb = interface.QuestionBase()
        flag, result = qb.create_question(request.user.id, question_type, question_title,
                                          question_content, ip=utils.get_clientip(request), is_hide_user=is_hide_user)
        if flag:
            return HttpResponseRedirect('/question/question_detail/%s' % result.id)
        else:
            error_msg = result
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def create_answer(request, question_id):
    content = request.POST.get('answer_content', '')

    qb = interface.QuestionBase()
    flag, result = qb.create_answer(question_id, request.user.id, content, ip=utils.get_clientip(request))
    if flag:
        return HttpResponseRedirect('/question/question_detail/%s' % question_id)
    else:
        return question_detail(request, question_id, error_msg=result, content=content)


def get_tags(request):
    name = request.REQUEST.get('search', '').strip()

    tags = [
        [1, 'aaaaa'],
        [2, 'AAbbb'],
        [3, u'大盘'],
        [4, u'个股'],
        [5, u'套现'],
        [6, u'网贷'],
        [7, u'信用卡'],
        [8, u'小额贷款'],
        [9, u'互联网金融'],
        [10, u'利率市场化'],
        [11, u'P2P借贷']
    ]
    match_tags = filter(lambda x: x[1].find(name) > -1, tags)
    format_tags = [[x[0], x[1], None, x[1]] for x in match_tags]
    return HttpResponse(json.dumps(format_tags))


def get_tags_by_question_type(request):
    '''
    根据提问类型获取对应的子话题
    '''
    tags = {
        '1': [
            {'id': 1, 'name': '大盘子话题1'},
            {'id': 2, 'name': '大盘子话题2'},
            {'id': 3, 'name': '大盘子话题3'}
        ],
        '2': [
            {'id': 4, 'name': '个股子话题1'},
            {'id': 5, 'name': '个股子话题2'},
            {'id': 6, 'name': '个股子话题3'}
        ],
        '3': [
            {'id': 7, 'name': '债券子话题1'},
            {'id': 8, 'name': '债券子话题2'},
        ],
        '4': [
            {'id': 9, 'name': '期权子话题1'},
            {'id': 10, 'name': '期权子话题2'},
            {'id': 11, 'name': '期权子话题3'},
            {'id': 12, 'name': '期权子话题4'}
        ]
    }

    result = []
    question_type = request.REQUEST.get('question_type', None)

    if question_type:
        result = tags[question_type]

    return HttpResponse(json.dumps(result))
