# -*- coding: utf-8 -*-

import json
# import urllib
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.question import interface
from www.misc.decorators import member_required, staff_required, common_ajax_response


qb = interface.QuestionBase()
ab = interface.AnswerBase()
lb = interface.LikeBase()
tb = interface.TopicBase()


def question_home(request, question_type=None, template_name='question/question_home.html'):
    from www.kaihu.interface import FriendlyLinkBase

    if question_type:
        question_type = interface.TopicBase().get_topic_by_id_or_domain(question_type)
        if not question_type:
            raise Http404
        questions = qb.get_questions_by_topic(question_type)
    else:
        questions = qb.get_all_questions_for_home_page()

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=10, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions)

    if not request.REQUEST.has_key('page') and not question_type:
        flinks = FriendlyLinkBase().get_friendly_link_by_link_type(link_type=3)  # 首页友链

    response = render_to_response(template_name, locals(), context_instance=RequestContext(request))
    response['Cache-Control'] = 'no-siteapp'
    return response


def question_detail(request, question_id, template_name='question/question_detail.html'):
    question = qb.get_question_by_id(question_id)
    if not question:
        raise Http404
    question = qb.format_quesitons([question, ], need_question_type=True, need_question_topics=True)[0]

    sort = request.REQUEST.get('sort', 'like_count')

    good_answers = ab.format_answers(ab.get_good_answers_by_question_id(question_id, "-" + sort), request.user, need_answer_likes=True)
    bad_answers = ab.format_answers(ab.get_bad_answers_by_question_id(question_id), request.user, need_answer_likes=True)
    good_answers_count = len(good_answers)
    bad_answers_count = len(bad_answers)

    # 从session中获取提示信息
    if request.session.has_key('error_msg'):
        error_msg = request.session['error_msg']
        del request.session['error_msg']
    if request.session.has_key('success_msg'):
        success_msg = request.session['success_msg']
        del request.session['success_msg']
    if request.session.has_key('answer_content'):
        answer_content = request.session['answer_content']
        del request.session['answer_content']
    if request.session.has_key('guide'):
        guide = request.session['guide']
        del request.session['guide']

    # 异步更新浏览次数
    from www.tasks import async_add_question_view_count
    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    if not("baidu" in user_agent or "spider" in user_agent):
        async_add_question_view_count(question.id)

    # 所有话题
    topics = json.dumps(tb.format_topics_for_ask_page(tb.get_all_topics_for_show()))
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def ask_question(request, template_name='question/ask_question.html'):
    if request.POST:
        question_title = request.POST.get('question_title', '').strip()
        question_content = request.POST.get('question_content', '').strip()
        is_hide_user = request.POST.get('is_hide_user')
        topic_ids = request.POST.getlist('tag')
        question_type = request.POST.get('question_type', '')
        topic_ids = topic_ids or [question_type, ]

        errcode, result = qb.create_question(request.user.id, question_title, question_content,
                                             ip=utils.get_clientip(request), is_hide_user=is_hide_user, topic_ids=topic_ids)
        if errcode == 0:
            request.session['guide'] = True
            return HttpResponseRedirect(result.get_url())
        else:
            error_msg = result

    # 所有话题
    topics = json.dumps(tb.format_topics_for_ask_page(tb.get_all_topics_for_show()))
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def modify_question(request, question_id):
    if request.POST:
        question_title = request.POST.get('question_title', '').strip()
        question_content = request.POST.get('question_content', '').strip()
        is_hide_user = request.POST.get('is_hide_user')
        topic_ids = request.POST.getlist('tag')
        question_type = request.POST.get('question_type', '')
        topic_ids = topic_ids or [question_type, ]

        errcode, result = qb.modify_question(question_id, request.user, question_title, question_content,
                                             ip=utils.get_clientip(request), is_hide_user=is_hide_user, topic_ids=topic_ids)
        if errcode == 0:
            request.session['success_msg'] = u'修改成功'
            return HttpResponseRedirect(result.get_url())
        else:
            request.session['error_msg'] = result
            return HttpResponseRedirect(qb.get_question_by_id(question_id).get_url())


@member_required
def modify_answer(request):
    if request.POST:
        question_id = request.POST.get('question_id')
        answer_id = request.POST.get('answer_id')
        edit_answer_content = request.POST.get('edit_answer_content', '').strip()

        errcode, result = ab.modify_answer(answer_id, request.user, edit_answer_content)
        if errcode == 0:
            request.session['success_msg'] = u'修改成功'
            return HttpResponseRedirect(result.question.get_url())
        else:
            request.session['error_msg'] = result
            return HttpResponseRedirect(qb.get_question_by_id(question_id).get_url())


@member_required
def create_answer(request, question_id):
    answer_content = request.POST.get('answer_content', '').strip()

    errcode, result = ab.create_answer(question_id, request.user.id, answer_content, ip=utils.get_clientip(request))
    if errcode == 0:
        return HttpResponseRedirect(result.question.get_url())
    else:
        request.session['error_msg'] = result
        request.session['answer_content'] = answer_content
        return HttpResponseRedirect(qb.get_question_by_id(question_id).get_url())


def important_question(request, template_name='question/important_question.html'):
    questions = qb.get_all_important_question()

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=10, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions, need_question_topics=True)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def topics(request, template_name="question/topics.html"):
    '''
    话题广场
    '''
    aqts = tb.get_all_question_type()
    question_type = int(request.REQUEST.get('question_type', 0))
    if question_type:
        topic = tb.get_topic_by_id_or_domain(question_type)
        if not topic:
            raise Http404
        topics = tb.get_topics_by_parent(topic)
    else:
        topics = tb.get_all_topics_for_show()
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def topic_question(request, topic_domain, template_name='question/topic_question.html'):
    """
    @note: 子话题页面
    """

    topic = tb.get_topic_by_id_or_domain(topic_domain)
    if not topic:
        raise Http404
    questions = qb.get_questions_by_topic(topic)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(questions, count=10, page=page_num).info
    questions = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    questions = qb.format_quesitons(questions)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def search(request):
    from www.account.interface import UserBase

    search_type = request.REQUEST.get('type', 'question').strip()
    if search_type not in ("question", "answer", "user"):
        raise Http404

    key_words = request.REQUEST.get('key_words', '').strip()
    if not key_words:
        info_msg = u"请输入搜索关键词"

    page_num = int(request.REQUEST.get('page', 1))
    page_num = 20 if page_num > 20 else page_num
    page_objs = None

    if search_type == "question":
        questions = qb.search_questions(key_words)
        page_objs = page.Cpt(questions, count=10, page=page_num).info
        questions = page_objs[0]
        questions = qb.format_quesitons(questions)

    if search_type == "answer":
        if len(key_words) < 4:
            info_msg = u"搜索回答最少输入4个字"
        else:
            answers = ab.search_answers(key_words)
            page_objs = page.Cpt(answers, count=10, page=page_num).info
            answers = page_objs[0]
            answers = ab.format_answers(answers)

    if search_type == "user":
        users = UserBase().search_users(key_words)
        page_objs = page.Cpt(users, count=10, page=page_num).info
        users = page_objs[0]
        users = [UserBase().format_user_with_count_info(user) for user in users]

    page_params = (page_objs[1], page_objs[4]) if page_objs else (1, 1)

    return render_to_response('question/search_%s.html' % search_type, locals(), context_instance=RequestContext(request))
# ===================================================ajax部分=================================================================#


@member_required
@common_ajax_response
def like_answer(request):
    answer_id = request.POST.get('answer_id', '').strip()
    return lb.like_it(answer_id, request.user.id, ip=utils.get_clientip(request))


@member_required
@common_ajax_response
def remove_answer(request):
    answer_id = request.POST.get('answer_id', '').strip()
    return ab.remove_answer(answer_id, request.user)


@member_required
@common_ajax_response
def remove_question(request):
    question_id = request.POST.get('question_id', '').strip()
    return qb.remove_question(question_id, request.user)


@staff_required
@common_ajax_response
def set_important(request):
    question_id = request.POST.get('question_id', '').strip()
    return qb.set_important(question_id, request.user)


@staff_required
@common_ajax_response
def cancel_important(request):
    question_id = request.POST.get('question_id', '').strip()
    return qb.cancel_important(question_id, request.user)


@member_required
@common_ajax_response
def set_answer_bad(request):
    answer_id = request.POST.get('answer_id', '').strip()
    return ab.set_answer_bad(answer_id, request.user)


@member_required
@common_ajax_response
def cancel_answer_bad(request):
    answer_id = request.POST.get('answer_id', '').strip()
    return ab.cancel_answer_bad(answer_id, request.user)


def get_topic_info_by_id(request):
    '''
    @note: 根据话题id获取名片信息
    '''
    topic_id = request.REQUEST.get('topic_id', '').strip()

    infos = {}
    if topic_id:
        topic = tb.get_topic_by_id_or_domain(topic_id)
        if topic:
            infos = dict(domain=topic.domain, name=topic.name, img=topic.get_img(), des=topic.des or u'',
                         question_count=topic.question_count)
    return HttpResponse(json.dumps(infos), mimetype='application/json')


def get_answer_like(request):
    '''
    @note: 获取回答对应的赞
    '''
    answer_id = request.REQUEST.get('answer_id', '').strip()

    data = []
    if answer_id:
        likes = lb.format_likes(lb.get_likes_by_answer(answer_id))
        data = [dict(user_id=like.from_user.id, user_nick=like.from_user.nick) for like in likes]
    return HttpResponse(json.dumps(data), mimetype='application/json')


def search_auto_complete(request):
    '''
    @note: 搜索自动补全
    '''
    from www.custom_tags.templatetags.custom_filters import str_display
    from www.account.interface import UserBase

    key = request.REQUEST.get('key', '').strip()
    data = []
    if key:
        users = UserBase().search_users(key)[:5]
        questions = qb.search_questions(key)[:5]
        i = 1
        for user in users:
            data.append(dict(type="user", value=str(i), data=user.nick, des=str_display((user.des or '').strip(), 30), avatar=user.get_avatar_65(), url=user.get_url()))
            i += 1

        for question in questions:
            data.append(dict(type="question", value=str(i), data=str_display(question.title, 25), answer_count=question.answer_count, url=question.get_url()))
            i += 1
    return HttpResponse(json.dumps(data), mimetype='application/json')
