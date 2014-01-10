# -*- coding: utf-8 -*-

import datetime
import time
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache
from www.question.models import Question, QuestionType, Answer


dict_err = {
    100: u'标题过于简单，稍微详述一下',
    101: u'标题过于冗长，稍微提炼一下',
    102: u'内容过于简单，稍微详述一下',
    103: u'内容过于冗长，稍微提炼一下',

    800: u'问题不存在或者已删除',
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


class QuestionBase(object):

    def __init__(self):
        pass

    def format_quesitons(self, questions):
        for question in questions:
            question.user = question.get_user()
        return questions

    def format_answers(self, answers):
        for answer in answers:
            answer.from_user = answer.get_from_user()
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
        return Answer.objects.filter(question=question_id, state=True)


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
