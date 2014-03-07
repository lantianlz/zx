# -*- coding: utf-8 -*-

import json
# import urllib
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.question import interface
from www.misc.decorators import member_required


qb = interface.QuestionBase()
ab = interface.AnswerBase()
lb = interface.LikeBase()
tb = interface.TagBase()


@member_required
def question_home(request, question_type=0, template_name='question/question_home.html'):
    questions = qb.get_questions_by_type(question_type_domain=question_type)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=3, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def tag_question(request, tag_domain, template_name='question/question_home.html'):
    """
    @note: 通过标签展现话题
    """

    tag = tb.get_tag_by_domain(tag_domain)
    questions = qb.get_questions_by_tag(tag)

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
    question = qb.get_question_by_id(question_id)
    question = qb.format_quesitons([question, ])[0]
    if not question:
        raise Http404

    answers = ab.get_answers_by_question_id(question_id)
    answers = ab.format_answers(answers, request.user)

    # 异步更新浏览次数
    from www.tasks import async_add_question_view_count
    async_add_question_view_count(question.id)

    question_tags = tb.get_tags_by_question(question)
    # 标签
    tags = json.dumps(tb.format_tags_for_ask_page(tb.get_all_tags()))
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def ask_question(request, template_name='question/ask_question.html'):
    if request.POST:
        question_type = int(request.POST.get('question_type', '0'))
        question_title = request.POST.get('question_title')
        question_content = request.POST.get('question_content')
        is_hide_user = request.POST.get('is_hide_user')
        tags = request.POST.getlist('tag')

        flag, result = qb.create_question(request.user.id, question_type, question_title, question_content,
                                          ip=utils.get_clientip(request), is_hide_user=is_hide_user, tags=tags)
        if flag:
            return HttpResponseRedirect('/question/question_detail/%s' % result.id)
        else:
            error_msg = result

    # 标签
    tags = json.dumps(tb.format_tags_for_ask_page(tb.get_all_tags()))
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def create_answer(request, question_id):
    content = request.POST.get('answer_content', '')

    flag, result = ab.create_answer(question_id, request.user.id, content, ip=utils.get_clientip(request))
    if flag:
        return HttpResponseRedirect('/question/question_detail/%s' % question_id)
    else:
        return question_detail(request, question_id, error_msg=result, content=content)


@member_required
def important_question(request, template_name='question/important_question.html'):
    questions = qb.get_all_important_question()

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=3, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

# ===================================================ajax部分=================================================================#


@member_required
def like_answer(request):
    answer_id = request.POST.get('answer_id', '')

    flag, result = lb.like_it(answer_id, request.user.id, ip=utils.get_clientip(request))
    r = dict(flag='0' if flag else '-1', result=result)
    return HttpResponse(json.dumps(r), mimetype='application/json')


@member_required
def remove_answer(request):
    answer_id = request.POST.get('answer_id', '')

    flag, result = ab.remove_answer(answer_id, request.user)
    r = dict(flag='0' if flag else '-1', result=result)
    return HttpResponse(json.dumps(r), mimetype='application/json')
