# -*- coding: utf-8 -*-

import datetime
import logging
from django.db import transaction

from common import utils, debug, cache
from www.question.models import Question, QuestionType, Answer, Like


dict_err = {
    100: u'标题过于简单，稍微详述一下',
    101: u'标题过于冗长，稍微提炼一下',
    102: u'内容过于简单，稍微详述一下',
    103: u'内容过于冗长，稍微提炼一下',
    104: u'喜欢一次足矣',

    800: u'问题不存在或者已删除',
    801: u'回答不存在或者已删除',
    998: u'参数缺失',
    999: u'系统错误',
    000: u'成功'
}

QUESTION_DB = 'question'


def question_required(func):
    def _decorator(self, question_id_or_object, *args, **kwargs):
        question = question_id_or_object
        if not isinstance(question_id_or_object, Question):
            try:
                question = Question.objects.get(id=question_id_or_object)
            except Question.DoesNotExist:
                return False, dict_err.get(800)
        return func(self, question, *args, **kwargs)
    return _decorator


def answer_required(func):
    def _decorator(self, answer_id_or_object, *args, **kwargs):
        answer = answer_id_or_object
        if not isinstance(answer_id_or_object, Question):
            try:
                answer = Answer.objects.select_related('question').get(id=answer_id_or_object)
            except Answer.DoesNotExist:
                return False, dict_err.get(801)
        return func(self, answer, *args, **kwargs)
    return _decorator


class QuestionBase(object):

    def __init__(self):
        pass

    def format_quesitons(self, questions):
        for question in questions:
            question.user = question.get_user()
        return questions

    def format_answers(self, answers, request_user=None):
        request_user_like_answer_ids = []
        if request_user and answers:
            request_user_likes = LikeBase().get_likes_by_question(answers[0].question, request_user.id)
            request_user_like_answer_ids = [l.answer_id for l in request_user_likes]

        for answer in answers:
            answer.from_user = answer.get_from_user()
            answer.is_request_user_like = (answer.id in request_user_like_answer_ids)   # 当前登录用户是否喜欢了改问题
        return answers

    def validate_title(self, title):
        if len(title) < 10:
            return False, dict_err.get(100)
        if len(title) > 128:
            return False, dict_err.get(101)
        return True, dict_err.get(000)

    def validate_content(self, content):
        if len(content) < 20:
            return False, dict_err.get(102)
        if len(content) > 65535:
            return False, dict_err.get(103)
        return True, dict_err.get(000)

    def create_question(self, user_id, question_type, question_title, question_content, ip='127.0.0.1', is_hide_user=None):
        # 防止xss漏洞
        question_title = utils.filter_script(question_title)
        question_content = utils.filter_script(question_content)

        flag, result = self.validate_title(question_title)
        if not flag:
            return False, result

        flag, result = self.validate_content(question_content)
        if not flag:
            return False, result

        if not all((int(question_type), question_title, question_content)):
            return False, dict_err.get(998)

        question = Question.objects.create(user_id=user_id, question_type_id=question_type,
                                           title=question_title, content=question_content,
                                           last_answer_time=datetime.datetime.now(), ip=ip,
                                           is_hide_user=True if is_hide_user else False)

        # todo 清理缓存、更新冗余信息等
        return True, question

    def get_questions(self, question_type_domain=None):
        ps = dict(state=True)
        if question_type_domain:
            ps.update(question_type=QuestionTypeBase().get_question_type_by_id_or_domain(question_type_domain))
        questions = Question.objects.filter(**ps)
        return questions

    def get_question_by_id(self, id):
        try:
            return Question.objects.select_related('question_type').get(id=id)
        except Question.DoesNotExist:
            return None

    @question_required
    @transaction.commit_manually(using=QUESTION_DB)
    def create_answer(self, question, from_user_id, content, ip=None):
        try:
            content = utils.filter_script(content)
            if not all((question, from_user_id, content)):
                transaction.rollback(using=QUESTION_DB)
                return False, dict_err.get(998)

            flag, result = self.validate_content(content)
            if not flag:
                transaction.rollback(using=QUESTION_DB)
                return False, result

            answer = Answer.objects.create(from_user_id=from_user_id, to_user_id=question.user_id, content=content,
                                           question=question, ip=ip)

            question.answer_count += 1
            question.last_answer_time = datetime.datetime.now()
            question.save()

            transaction.commit(using=QUESTION_DB)
            return True, answer
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return False, dict_err.get(999)

    def get_answers_by_question_id(self, question_id):
        return Answer.objects.select_related('question').filter(question=question_id, state=True)


class QuestionTypeBase(object):

    def get_all_question_type(self, cached=True):
        key = 'all_question_type'
        cache_obj = cache.Cache(config=cache.CACHE_STATIC)
        qts = cache_obj.get(key)
        if not qts or not cached:
            qts = QuestionType.objects.filter(state=True).order_by('-sort_num', 'id')
            cache_obj.set(key, qts)
        return qts

    def get_question_type_by_id_or_domain(self, id_or_domain):
        aqts = self.get_all_question_type()
        for aqt in aqts:
            if str(aqt.id) == str(id_or_domain) or str(aqt.domain) == str(id_or_domain):
                return aqt


class LikeBase(object):

    '''
    @note: “喜欢”模块封装
    '''
    @answer_required
    @transaction.commit_manually(QUESTION_DB)
    def like_it(self, answer, from_user_id, ip):
        '''
        @note: 喜欢操作封装
        '''
        try:
            assert all((answer, from_user_id, ip))
            from django.db.models import F
            is_anonymous = False
            if from_user_id:
                if Like.objects.filter(from_user_id=from_user_id, answer=answer):
                    transaction.rollback(QUESTION_DB)
                    return False, dict_err.get(104)
            else:
                from_user_id = ''
                is_anonymous = False
                if Like.objects.filter(ip=ip, answer=answer):
                    transaction.rollback(QUESTION_DB)
                    return False, dict_err.get(104)

            Like.objects.create(answer=answer, question=answer.question, is_anonymous=is_anonymous,
                                from_user_id=from_user_id, to_user_id=answer.question.get_user().id, ip=ip)
            Answer.objects.filter(id=answer.id).update(like_count=F('like_count') + 1)

            transaction.commit(QUESTION_DB)
            return True, dict_err.get(000)
        except Exception, e:
            logging.error(debug.get_debug_detail(e))
            transaction.rollback(QUESTION_DB)
            return False, str(e)

    def get_likes_by_question(self, question, user_id=None, ip=None):
        '''
        @note: 获取某个提问下的问题的所有喜欢，用于前端判断当前登录用户是否喜欢了该回答，匿名用户采用ip判断
        '''
        ps = dict(question=question)
        if user_id:
            ps.update(dict(from_user_id=user_id))
        if ip:
            ps.update(dict(ip=ip, is_anonymous=True))
        return Like.objects.filter(**ps)
