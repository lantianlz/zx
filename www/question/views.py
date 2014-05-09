# -*- coding: utf-8 -*-

import json
# import urllib
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.question import interface
from www.misc.decorators import member_required, staff_required


qb = interface.QuestionBase()
ab = interface.AnswerBase()
lb = interface.LikeBase()
tb = interface.TagBase()


# @member_required
def question_home(request, question_type=None, template_name='question/question_home.html'):
    if question_type:
        question_type = interface.QuestionTypeBase().get_question_type_by_id_or_domain(question_type)
        if not question_type:
            raise Http404
    questions = qb.get_questions_by_type(question_type_domain=question_type)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=10, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# @member_required
def question_detail(request, question_id, template_name='question/question_detail.html',
                    error_msg=None, success_msg=None, answer_content=''):
    question = qb.get_question_by_id(question_id)
    if not question:
        raise Http404
    question = qb.format_quesitons([question, ])[0]

    good_answers = ab.format_answers(ab.get_good_answers_by_question_id(question_id), request.user)
    bad_answers = ab.format_answers(ab.get_bad_answers_by_question_id(question_id), request.user)
    good_answers_count = len(good_answers)
    bad_answers_count = len(bad_answers)

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
        question_title = request.POST.get('question_title', '').strip()
        question_content = request.POST.get('question_content', '').strip()
        is_hide_user = request.POST.get('is_hide_user')
        tags = request.POST.getlist('tag')

        flag, result = qb.create_question(request.user.id, question_type, question_title, question_content,
                                          ip=utils.get_clientip(request), is_hide_user=is_hide_user, tags=tags)
        if flag:
            return HttpResponseRedirect(result.get_url())
        else:
            error_msg = result

    # 标签
    tags = json.dumps(tb.format_tags_for_ask_page(tb.get_all_tags()))
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def modify_question(request, question_id):
    if request.POST:
        question_type = int(request.POST.get('question_type', '0'))
        question_title = request.POST.get('question_title', '').strip()
        question_content = request.POST.get('question_content', '').strip()
        is_hide_user = request.POST.get('is_hide_user')
        tags = request.POST.getlist('tag')

        flag, result = qb.modify_question(question_id, request.user, question_type, question_title, question_content,
                                          ip=utils.get_clientip(request), is_hide_user=is_hide_user, tags=tags)
        if flag:
            return question_detail(request, question_id, success_msg=u'修改成功')
            # return HttpResponseRedirect(result.get_url())
        else:
            return question_detail(request, question_id, error_msg=result)
    else:
        return question_detail(request, question_id)


@member_required
def modify_answer(request):
    if request.POST:
        question_id = request.POST.get('question_id')
        answer_id = request.POST.get('answer_id')
        edit_answer_content = request.POST.get('edit_answer_content', '').strip()

        flag, result = ab.modify_answer(answer_id, request.user, edit_answer_content)
        if flag:
            return question_detail(request, question_id, success_msg=u'修改成功')
        else:
            return question_detail(request, question_id, error_msg=result)


@member_required
def create_answer(request, question_id):
    answer_content = request.POST.get('answer_content', '').strip()

    flag, result = ab.create_answer(question_id, request.user.id, answer_content, ip=utils.get_clientip(request))
    if flag:
        return HttpResponseRedirect(result.question.get_url())
    else:
        return question_detail(request, question_id, error_msg=result, answer_content=answer_content)


# @member_required
def important_question(request, template_name='question/important_question.html'):
    questions = qb.get_all_important_question()

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=10, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def topics(request, template_name="question/topics.html"):
    '''
    话题广场
    '''
    aqts = interface.QuestionTypeBase().get_all_question_type()
    question_type = request.REQUEST.get('question_type')
    if question_type:
        question_type = int(question_type)
        tags = tb.get_tags_by_question_type(question_type)
    else:
        tags = tb.get_all_tags()
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def topic_question(request, tag_domain, template_name='question/topic_question.html'):
    """
    @note: 子话题页面
    """

    tag = tb.get_tag_by_domain(tag_domain)
    if not tag:
        raise Http404
    questions = qb.get_questions_by_tag(tag)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=10, page=page_num).info
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


@member_required
def remove_question(request):
    question_id = request.POST.get('question_id', '')

    flag, result = qb.remove_question(question_id, request.user)
    r = dict(flag='0' if flag else '-1', result=result)
    return HttpResponse(json.dumps(r), mimetype='application/json')


@staff_required
def set_important(request):
    question_id = request.POST.get('question_id', '')

    flag, result = qb.set_important(question_id, request.user)
    r = dict(flag='0' if flag else '-1', result=result)
    return HttpResponse(json.dumps(r), mimetype='application/json')


@staff_required
def cancel_important(request):
    question_id = request.POST.get('question_id', '')

    flag, result = qb.cancel_important(question_id, request.user)
    r = dict(flag='0' if flag else '-1', result=result)
    return HttpResponse(json.dumps(r), mimetype='application/json')


@member_required
def set_answer_bad(request):
    answer_id = request.POST.get('answer_id', '')

    flag, result = ab.set_answer_bad(answer_id, request.user)
    r = dict(flag='0' if flag else '-1', result=result)
    return HttpResponse(json.dumps(r), mimetype='application/json')


@member_required
def cancel_answer_bad(request):
    answer_id = request.POST.get('answer_id', '')

    flag, result = ab.cancel_answer_bad(answer_id, request.user)
    r = dict(flag='0' if flag else '-1', result=result)
    return HttpResponse(json.dumps(r), mimetype='application/json')


def get_topic_info_by_id(request):
    '''
    @note:根据话题id获取名片信息
    '''
    topic_id = request.REQUEST.get('topic_id', None)

    infos = {}

    if topic_id:
        tag = tb.get_tag_by_id(topic_id)
        if tag:
            infos = dict(domain=tag.domain, name=tag.name, img=tag.get_img(), des=tag.des or u'暂无话题介绍',
                         tag_question_count=tag.get_tag_question_count())

    return HttpResponse(json.dumps(infos), mimetype='application/json')
