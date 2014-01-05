# -*- coding: utf-8 -*-

import datetime
import time
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache
from www.question.models import Question, QuestionType


dict_err = {
    100: u'',

    998: u'参数缺失',
    999: u'系统错误',
    000: u'成功'
}


class QuestionBase(object):

    def __init__(self):
        pass

    def create_question(self, question_type, question_title, question_content):
        # 防止xss漏洞
        question_title = utils.filter_script(question_title)
        question_content = utils.filter_script(question_content)

        if not all((question_type, question_title, question_content)):
            return False, dict_err.get(998)

        question = Question.objects.create(question_type_id=question_type, title=question_title, question_content=question_content)
        return True, question


class QuestionTypeBase(object):

    def get_all_question_type(self, cached=True):
        key = 'all_question_type'
        cache_obj = cache.Cache(config=cache.CACHE_STATIC)
        qts = cache_obj.get(key)
        if not qts or not cached:
            qts = QuestionType.objects.filter(state=True).order_by('-sort_num', 'id')
            cache_obj.set(key, qts)
        return qts
