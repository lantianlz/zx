# -*- coding: utf-8 -*-

import datetime
import logging
from django.db import transaction
from django.db.models import F

from common import utils, debug, cache
from www.account.interface import UserBase
from www.message.interface import UnreadCountBase
from www.question.models import Question, QuestionType, Answer, Like, Tag, TagQuestion, AtAnswer


dict_err = {
    100: u'标题过于简单，稍微详述一下',
    101: u'标题过于冗长，稍微提炼一下',
    102: u'内容过于简单，稍微详述一下',
    103: u'内容过于冗长，稍微提炼一下',
    104: u'喜欢一次足矣',
    105: u'自己赞自己的回答是自恋的表现哦，暂不支持',

    800: u'问题不存在或者已删除',
    801: u'回答不存在或者已删除',
    802: u'绝对不会让你得逞的，因为你没得权限',

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
                question = Question.objects.get(id=question_id_or_object, state=True)
            except Question.DoesNotExist:
                return False, dict_err.get(800)
        return func(self, question, *args, **kwargs)
    return _decorator


def question_admin_required(func):
    def _decorator(self, question, user, *args, **kwargs):
        flag, question = QuestionBase().get_question_admin_permission(question, user)
        if not flag:
            return False, dict_err.get(802)
        return func(self, question, user, *args, **kwargs)
    return _decorator


def answer_required(func):
    def _decorator(self, answer_id_or_object, *args, **kwargs):
        answer = answer_id_or_object
        if not isinstance(answer_id_or_object, Question):
            try:
                answer = Answer.objects.select_related('question').get(id=answer_id_or_object, state=True)
            except Answer.DoesNotExist:
                return False, dict_err.get(801)
        return func(self, answer, *args, **kwargs)
    return _decorator


def answer_admin_required(func):
    def _decorator(self, answer, user, *args, **kwargs):
        flag, answer = AnswerBase().get_answer_admin_permission(answer, user)
        if not flag:
            return False, dict_err.get(802)
        return func(self, answer, user, *args, **kwargs)
    return _decorator


class QuestionBase(object):

    def __init__(self):
        pass

    def format_quesitons(self, questions):
        for question in questions:
            question.user = question.get_user()
            question.content = utils.filter_script(question.content)
        return questions

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

    def validata_question_element(self, question_type, question_title, question_content):
        flag, result = self.validate_title(question_title)
        if not flag:
            return False, result

        flag, result = self.validate_content(question_content)
        if not flag:
            return False, result

        if not all((int(question_type), question_title, question_content)):
            return False, dict_err.get(998)

        return True, dict_err.get(000)

    @transaction.commit_manually(using=QUESTION_DB)
    def create_question(self, user_id, question_type, question_title, question_content,
                        ip='127.0.0.1', is_hide_user=None, tags=[]):
        try:
            # 防止xss漏洞
            question_title = utils.filter_script(question_title)
            question_content = utils.filter_script(question_content)

            flag, result = self.validata_question_element(question_type, question_title, question_content)
            transaction.rollback(using=QUESTION_DB)
            if not flag:
                transaction.rollback(using=QUESTION_DB)
                return False, result

            question = Question.objects.create(user_id=user_id, question_type_id=question_type,
                                               title=question_title, content=question_content,
                                               last_answer_time=datetime.datetime.now(), ip=ip,
                                               is_hide_user=True if is_hide_user else False)

            # 创建话题和tags关系
            for tag in tags:
                try:
                    TagQuestion.objects.create(tag_id=tag, question=question)
                except:
                    pass

            # 更新用户话题数信息
            cache.get_or_update_data_from_cache('question_count_%s' % user_id, False, 3600 * 24,
                                                self.get_user_question_count, user_id)

            transaction.commit(using=QUESTION_DB)
            return True, question
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return False, dict_err.get(999)

    @question_admin_required
    @transaction.commit_manually(using=QUESTION_DB)
    def modify_question(self, question, user, question_type, question_title, question_content,
                        ip='127.0.0.1', is_hide_user=None, tags=[]):
        try:
            # 防止xss漏洞
            question_title = utils.filter_script(question_title)
            question_content = utils.filter_script(question_content)

            flag, result = self.validata_question_element(question_type, question_title, question_content)
            if not flag:
                transaction.rollback(using=QUESTION_DB)
                return False, result

            question.question_type_id = question_type
            question.title = question_title
            question.content = question_content
            question.ip = ip
            if is_hide_user:
                question.is_hide_user = True
            question.save()

            # 创建话题和tags关系
            new_tags = [str(tag_id) for tag_id in [tq.tag_id for tq in TagQuestion.objects.filter(question=question)]]
            new_tags.sort()
            tags.sort()
            if tags != new_tags:
                TagQuestion.objects.filter(question=question).delete()
                for tag in tags:
                    try:
                        TagQuestion.objects.create(tag_id=tag, question=question)
                    except:
                        pass

            transaction.commit(using=QUESTION_DB)
            return True, question
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return False, dict_err.get(999)

    def add_question_view_count(self, question_id):
        '''
        @note: 更新浏览次数
        '''
        Question.objects.filter(id=question_id).update(views_count=F('views_count') + 1)

    @question_admin_required
    @transaction.commit_manually(using=QUESTION_DB)
    def remove_question(self, question, user):
        try:
            question.state = False
            question.save()

            # 更新用户回答统计总数
            cache.get_or_update_data_from_cache('question_count_%s' % question.user_id, False, 3600 * 24,
                                                self.get_user_question_count, question.user_id)

            transaction.commit(using=QUESTION_DB)
            return True, dict_err.get(000)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return False, dict_err.get(999)

    def get_question_by_user_id(self, user_id):
        return Question.objects.filter(user_id=user_id, state=True)

    def get_questions_by_type(self, question_type_domain=None):
        ps = dict(state=True)
        if question_type_domain:
            ps.update(question_type=QuestionTypeBase().get_question_type_by_id_or_domain(question_type_domain))
        questions = Question.objects.filter(**ps)
        return questions

    def get_questions_by_tag(self, tag_object_or_domain):
        tag = TagBase().get_tag_by_domain(tag_object_or_domain) if not isinstance(tag_object_or_domain, Tag)\
            else tag_object_or_domain
        if tag:
            return [tq.question for tq in TagQuestion.objects.select_related('question')
                    .filter(tag=tag).order_by("-question__sort_num", '-question__like_count', "-question__last_answer_time")]
        else:
            return []

    def get_question_by_id(self, id):
        try:
            return Question.objects.select_related('question_type').get(id=id, state=True)
        except Question.DoesNotExist:
            return None

    def get_user_question_count(self, user_id):
        return self.get_question_by_user_id(user_id).count()

    def get_user_qa_count_info(self, user_id):
        '''
        @note: 获取问、答、被赞统计信息
        '''
        user_question_count = cache.get_or_update_data_from_cache('question_count_%s' % user_id, True, 3600 * 24,
                                                                  self.get_user_question_count, user_id)
        user_answer_count = cache.get_or_update_data_from_cache('answer_count_%s' % user_id, True, 3600 * 24,
                                                                AnswerBase().get_user_sended_answers_count, user_id)
        user_liked_count = cache.get_or_update_data_from_cache('liked_count_%s' % user_id, True, 3600 * 24,
                                                               LikeBase().get_user_liked_count, user_id)
        return user_question_count, user_answer_count, user_liked_count

    def get_all_important_question(self):
        return Question.objects.filter(is_important=True, state=True).order_by('-id')

    @question_required
    def get_question_admin_permission(self, question, user):
        # 返回question值用于question对象赋值
        return question.user_id == user.id or user.is_staff(), question

    @question_required
    def set_important(self, question, user):
        question.is_important = True
        question.save()
        return True, dict_err.get(000)

    @question_required
    def cachel_important(self, question, user):
        question.is_important = False
        question.save()

        return True, dict_err.get(000)


class AnswerBase(object):

    def format_answers(self, answers, request_user=None):
        request_user_like_answer_ids = []
        if request_user and answers:
            request_user_likes = LikeBase().get_likes_by_question(answers[0].question, request_user.id)
            request_user_like_answer_ids = [l.answer_id for l in request_user_likes]

        for answer in answers:
            answer.from_user = answer.get_from_user()
            answer.content = utils.replace_at_html(answer.content)
            answer.is_request_user_like = (answer.id in request_user_like_answer_ids)   # 当前登录用户是否喜欢了改问题
        return answers

    @question_required
    @transaction.commit_manually(using=QUESTION_DB)
    def create_answer(self, question, from_user_id, content, ip=None):
        try:
            content = utils.filter_script(content)
            if not all((question, from_user_id, content)):
                transaction.rollback(using=QUESTION_DB)
                return False, dict_err.get(998)

            flag, result = QuestionBase().validate_content(content)
            if not flag:
                transaction.rollback(using=QUESTION_DB)
                return False, result

            to_user_id = question.user_id
            answer = Answer.objects.create(from_user_id=from_user_id, to_user_id=to_user_id, content=content,
                                           question=question, ip=ip)

            # 添加at信息
            if content.find('@') != -1:
                at_usernicks = utils.select_at(content)
                for nick in at_usernicks:
                    at_user = UserBase().get_user_by_nick(nick)
                    if at_user:
                        AtAnswer.objects.create(answer=answer, user_id=at_user.id)
                        if at_user.id != from_user_id and at_user.id != to_user_id:
                            # 发送未读消息数通知
                            UnreadCountBase().update_unread_count(at_user.id, code='at_answer')

            # 更新未读消息
            if from_user_id != to_user_id:
                UnreadCountBase().update_unread_count(to_user_id, code='received_answer')

            # 更新用户回答统计总数
            cache.get_or_update_data_from_cache('answer_count_%s' % from_user_id, False, 3600 * 24,
                                                self.get_user_sended_answers_count, from_user_id)

            # 更新回答数冗余信息
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

    def get_user_received_answer(self, user_id):
        return Answer.objects.select_related('question').filter(to_user_id=user_id, state=True)\
            .exclude(from_user_id=user_id).order_by('-id')

    def get_user_sended_answer(self, user_id):
        return Answer.objects.select_related('question').filter(from_user_id=user_id, state=True).order_by('-id')

    def get_at_answers(self, user_id):
        return [aa.answer for aa in AtAnswer.objects.select_related('answer').filter(user_id=user_id)]

    def get_user_sended_answers_count(self, user_id):
        return self.get_user_sended_answer(user_id).count()

    @answer_required
    def get_answer_admin_permission(self, answer, user):
        # 返回answer值用于answer对象赋值
        return answer.from_user_id == user.id or answer.to_user_id == user.id or user.is_staff(), answer

    @answer_admin_required
    @transaction.commit_manually(using=QUESTION_DB)
    def remove_answer(self, answer, user):
        try:
            answer.state = False
            answer.save()

            answer.question.answer_count -= 1
            answer.question.save()

            AtAnswer.objects.filter(user_id=user.id).delete()

            # 更新用户回答统计总数
            cache.get_or_update_data_from_cache('answer_count_%s' % answer.from_user_id, False, 3600 * 24,
                                                self.get_user_sended_answers_count, answer.from_user_id)

            transaction.commit(using=QUESTION_DB)
            return True, dict_err.get(000)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return False, dict_err.get(999)


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

            # 不支持自赞
            to_user_id = answer.from_user_id
            if from_user_id == to_user_id:
                transaction.rollback(QUESTION_DB)
                return False, dict_err.get(105)

            Like.objects.create(answer=answer, question=answer.question, is_anonymous=is_anonymous,
                                from_user_id=from_user_id, to_user_id=to_user_id, ip=ip)
            Answer.objects.filter(id=answer.id).update(like_count=F('like_count') + 1)

            # 更新未读消息
            from www.message.interface import UnreadCountBase
            UnreadCountBase().update_unread_count(to_user_id, code='received_like')

            # 更新被赞次数
            cache.get_or_update_data_from_cache('liked_count_%s' % to_user_id, False, 3600 * 24,
                                                self.get_user_liked_count, to_user_id)

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

    def get_to_user_likes(self, user_id):
        return Like.objects.select_related('question').filter(to_user_id=user_id, is_anonymous=False)

    def format_likes(self, likes):
        for like in likes:
            like.from_user = UserBase().get_user_by_id(like.from_user_id)
        return likes

    def get_user_liked_count(self, user_id):
        return self.get_to_user_likes(user_id).count()


class TagBase(object):

    def get_all_tags(self, cached=True):
        key = 'all_question_tag'
        cache_obj = cache.Cache(config=cache.CACHE_STATIC)
        tags = cache_obj.get(key)
        if not tags or not cached:
            tags = Tag.objects.filter(state=True)
            cache_obj.set(key, tags)
        return tags

    def get_tag_by_domain(self, domain):
        tags = self.get_all_tags()
        for tag in tags:
            if tag.domain == domain:
                return tag

    def get_tags_by_question_type(self, question_type):
        return self.get_all_tags().filter(question_type=question_type)

    def get_tags_by_question(self, question):
        return [tq.tag for tq in TagQuestion.objects.select_related('tag').filter(question=question)]

    def format_tags_for_ask_page(self, tags):
        ftags = {}
        for tag in tags:
            if str(tag.question_type_id) not in ftags:
                ftags[str(tag.question_type_id)] = [(tag.id, tag.name), ]
            else:
                ftags[str(tag.question_type_id)].append((tag.id, tag.name),)
        return ftags
