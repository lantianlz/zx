# -*- coding: utf-8 -*-

import datetime
from django.db import transaction
from django.db.models import F

from common import utils, debug, cache
from www.misc.decorators import cache_required
from www.misc import consts
from www.tasks import async_send_email
from www.timeline.interface import FeedBase
from www.message.interface import UnreadCountBase
from www.account.interface import UserBase
from www.account.interface import UserCountBase
from www.question.models import Question, Answer, Like, AtAnswer, AnswerBad
from www.question.models import ImportantQuestion, Topic, TopicQuestion


dict_err = {
    20100: u'标题过于简单，稍微详述一下',
    20101: u'标题过于冗长，稍微提炼一下',
    20102: u'内容过于简单，稍微详述一下',
    20103: u'内容过于冗长，稍微提炼一下',
    20104: u'喜欢一次足矣',
    20105: u'自己赞自己的回答是自恋的表现哦，暂不支持',
    20106: u'不要重复给没有帮助的选项哦',
    20107: u'话题的domain或name重复',
    20108: u'父话题的level必须大于等于当前话题level',

    20800: u'问题不存在或者已删除',
    20801: u'回答不存在或者已删除',
    20802: u'绝对不会让你得逞的，因为你没得权限',
}
dict_err.update(consts.G_DICT_ERROR)

QUESTION_DB = 'question'


def question_required(func):
    def _decorator(self, question_id_or_object, *args, **kwargs):
        question = question_id_or_object
        if not isinstance(question_id_or_object, Question):
            try:
                question = Question.objects.get(id=question_id_or_object, state=True)
            except Question.DoesNotExist:
                return 20800, dict_err.get(20800)
        return func(self, question, *args, **kwargs)
    return _decorator


def question_admin_required(func):
    def _decorator(self, question, user, *args, **kwargs):
        flag, question = QuestionBase().get_question_admin_permission(question, user)
        if not flag:
            return 20802, dict_err.get(20802)
        return func(self, question, user, *args, **kwargs)
    return _decorator


def answer_required(func):
    def _decorator(self, answer_id_or_object, *args, **kwargs):
        answer = answer_id_or_object
        if not isinstance(answer_id_or_object, Question):
            try:
                answer = Answer.objects.select_related('question').get(id=answer_id_or_object, state=True)
            except Answer.DoesNotExist:
                return 20801, dict_err.get(20801)
        return func(self, answer, *args, **kwargs)
    return _decorator


def answer_admin_required(func):
    def _decorator(self, answer, user, *args, **kwargs):
        flag, answer = AnswerBase().get_answer_admin_permission(answer, user)
        if not flag:
            return 20802, dict_err.get(20802)
        return func(self, answer, user, *args, **kwargs)
    return _decorator


class QuestionBase(object):

    def __init__(self):
        pass

    def format_quesitons(self, questions, need_question_type=False, need_question_topics=False):
        for question in questions:
            question.user = question.get_user()
            question.content = utils.filter_script(question.content)
            if need_question_type:
                question.question_type = TopicBase().get_topic_level1_by_question(question)
            if need_question_topics:
                question.question_topics = TopicBase().get_topics_by_question(question)
        return questions

    def validate_title(self, title):
        if len(title) < 10:
            return 20100, dict_err.get(20100)
        if len(title) > 128:
            return 20101, dict_err.get(20101)
        return 0, dict_err.get(0)

    def validate_content(self, content, min_len=10):
        if len(content) < min_len:
            return 20102, dict_err.get(20102)
        if len(content) > 65535:
            return 20103, dict_err.get(20103)
        return 0, dict_err.get(0)

    def validata_question_element(self, question_title, question_content):
        errcode, errmsg = self.validate_title(question_title)
        if not errcode == 0:
            return errcode, errmsg

        errcode, errmsg = self.validate_content(question_content, min_len=2)
        if not errcode == 0:
            return errcode, errmsg

        if not all((question_title, question_content)):
            return 99800, dict_err.get(99800)

        return 0, dict_err.get(0)

    @transaction.commit_manually(using=QUESTION_DB)
    def create_question(self, user_id, question_title, question_content,
                        ip='127.0.0.1', is_hide_user=None, topic_ids=[]):
        try:
            # 防止xss漏洞
            question_title = utils.filter_script(question_title)
            question_content = utils.filter_script(question_content)

            errcode, errmsg = self.validata_question_element(question_title, question_content)
            if not errcode == 0:
                transaction.rollback(using=QUESTION_DB)
                return errcode, errmsg

            is_hide_user = True if is_hide_user else False
            question = Question.objects.create(user_id=user_id, title=question_title, content=question_content,
                                               last_answer_time=datetime.datetime.now(), ip=ip,
                                               is_hide_user=is_hide_user, is_silence=self.get_question_is_silence_by_tags(topic_ids))

            # 创建话题和topics关系
            TopicBase().create_topic_question_relation(question, topic_ids)

            # 更新用户话题数信息
            UserCountBase().update_user_count(user_id=user_id, code='user_question_count')

            # 发送feed
            if not is_hide_user and not question.is_silence:
                FeedBase().create_feed(user_id, feed_type=1, obj_id=question.id)

            transaction.commit(using=QUESTION_DB)
            return 0, question
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    @question_admin_required
    @transaction.commit_manually(using=QUESTION_DB)
    def modify_question(self, question, user, question_title, question_content,
                        ip='127.0.0.1', is_hide_user=None, topic_ids=[]):
        try:
            # 防止xss漏洞
            question_title = utils.filter_script(question_title)
            question_content = utils.filter_script(question_content)

            errcode, errmsg = self.validata_question_element(question_title, question_content)
            if not errcode == 0:
                transaction.rollback(using=QUESTION_DB)
                return errcode, errmsg

            question.title = question_title
            question.content = question_content
            question.ip = ip
            if is_hide_user:
                question.is_hide_user = True
            question.is_silence = self.get_question_is_silence_by_tags(topic_ids)
            question.save()

            # 创建话题和topics关系
            TopicBase().create_topic_question_relation(question, topic_ids)

            # 更新summary
            self.get_question_summary_by_id(question, must_update_cache=True)

            transaction.commit(using=QUESTION_DB)
            return 0, question
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    def add_question_view_count(self, question_id):
        '''
        @note: 更新浏览次数
        '''
        Question.objects.filter(id=question_id).update(views_count=F('views_count') + 1)

    def get_question_is_silence_by_tags(self, topic_ids):
        '''
        @note: 获取提问是否为静默状态
        '''
        tb = TopicBase()
        topics = [tb.get_topic_by_id_or_domain(topic_id) for topic_id in topic_ids]
        for topic in topics:
            # 三类话题静默，之后改成在话题增加属性进行控制
            if topic and topic.state == 2:
                return True
        return False

    @question_admin_required
    @transaction.commit_manually(using=QUESTION_DB)
    def remove_question(self, question, user):
        try:
            question.state = False
            question.save()

            # 更新话题的提问数
            TopicBase().update_topic_question_count(question, operate='minus')

            # 更新用户话题数信息
            UserCountBase().update_user_count(user_id=question.user_id, code='user_question_count', operate='minus')

            # 更新timeline
            FeedBase().remove_feed(question.user_id, question.id, feed_type=1)

            transaction.commit(using=QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    def get_question_by_id(self, id, need_state=True):
        try:
            ps = dict(id=id)
            if need_state:
                ps.update(dict(state=True))
            return Question.objects.get(**ps)
        except Question.DoesNotExist:
            return None

    def get_questions_by_user_id(self, user_id):
        return Question.objects.filter(user_id=user_id, state=True)

    def get_user_question_count(self, user_id):
        return self.get_questions_by_user_id(user_id).count()

    def get_all_questions_for_home_page(self):
        return Question.objects.filter(is_silence=False, state=True)

    def get_questions_by_topic(self, topic_id_or_object):
        question_type = topic_id_or_object if isinstance(topic_id_or_object, Topic) else \
            TopicBase().get_topic_by_id_or_domain(topic_id_or_object)
        return [tq.question for tq in TopicQuestion.objects.select_related('question')
                .filter(topic=question_type, question__state=True).order_by("-question__sort_num", '-question__like_count', "-question__last_answer_time")]

    def get_all_important_question(self):
        questions = []
        important_questions = ImportantQuestion.objects.select_related('question').filter(question__state=True)
        for iq in important_questions:
            for attr in ['img', 'img_alt', 'sort_num', 'operate_user_id']:
                question = iq.question
                setattr(question, attr, getattr(iq, attr))

            question.author = iq.get_author()
            question.iq_title = iq.title or question.title
            question.iq_summary = iq.summary or question.get_summary()

            questions.append(question)
        return questions

    def get_important_question_by_title(self, title):
        '''
        根据标题查询精选
        '''
        important_questions = ImportantQuestion.objects.select_related('question').filter(question__state=True)

        if title:
            important_questions = important_questions.filter(question__title=title)

        for iq in important_questions:
            question = iq.question
            question.user = question.get_user()

        return important_questions

    def get_important_question_by_question_id(self, question_id):
        '''
        根据提问id查询精选
        '''
        iq = ImportantQuestion.objects.filter(question__id=question_id)
        if iq:
            iq = iq[0]
            question = iq.question
            question.user = question.get_user()
        return iq

    @question_required
    def get_question_admin_permission(self, question, user):
        # 返回question值用于question对象赋值
        return question.user_id == user.id or user.is_staff(), question

    @question_required
    @transaction.commit_manually(using=QUESTION_DB)
    def set_important(self, question, user, title, summary, author_user_id=None, img='', img_alt=None, sort_num=0):
        try:
            if author_user_id and not UserBase().get_user_by_id(author_user_id):
                transaction.rollback(using=QUESTION_DB)
                return 99600, dict_err.get(99600)

            try:
                assert question and user and title and summary
            except:
                transaction.rollback(using=QUESTION_DB)
                return 99800, dict_err.get(99800)

            question.is_important = True
            question.save()

            ps = dict(operate_user_id=user.id, img=img, img_alt=img_alt, sort_num=sort_num, title=title,
                      summary=summary, author_user_id=author_user_id)

            if not ImportantQuestion.objects.filter(question=question):
                ImportantQuestion.objects.create(question=question, **ps)
            else:
                ImportantQuestion.objects.filter(question=question).update(**ps)
            transaction.commit(using=QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    @question_required
    @transaction.commit_manually(using=QUESTION_DB)
    def cancel_important(self, question, user):
        try:
            question.is_important = False
            question.save()

            ImportantQuestion.objects.filter(question=question).delete()
            transaction.commit(using=QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    @cache_required(cache_key='question_summary_%s', expire=3600)
    def get_question_summary_by_id(self, question_id_or_object, must_update_cache=False):
        '''
        @note: 获取提问摘要信息，用于feed展现
        '''
        question = self.get_question_by_id(question_id_or_object, need_state=False) if not isinstance(question_id_or_object, Question) else question_id_or_object
        question_summary = {}
        if question:
            question_summary = dict(question_id=question.id, question_title=question.title,
                                    question_summary=question.get_summary(), question_answer_count=question.answer_count)
        return question_summary

    def get_question_by_title(self, title):
        '''
        根据标题查询提问
        '''
        questions = []
        if title:
            questions = Question.objects.filter(title=title)

        return self.format_quesitons(questions)

    def get_all_questions_by_order_type(self, order):
        '''
        根据统计数据排序
        '''
        return self.format_quesitons(Question.objects.all().order_by('-' + order))

    def get_questions_by_range_date(self, start_date, end_date):
        '''
        查询指定区间的提问
        '''
        return Question.objects.filter(create_time__range=(start_date, end_date))

    def search_questions(self, title):
        if not title:
            return []
        return Question.objects.filter(title__icontains=title, state=True)[:200]


class AnswerBase(object):

    def format_answers(self, answers, request_user=None, need_answer_likes=False):
        request_user_like_answer_ids = []
        request_user_bads = []
        if request_user and answers:
            request_user_likes = LikeBase().get_likes_by_question(answers[0].question, request_user.id)
            request_user_like_answer_ids = [l.answer_id for l in request_user_likes]    # 用户是否赞了该问题
            request_user_bads = [ab.answer_id for ab in AnswerBad.objects.filter(user_id=request_user.id)]

        lb = LikeBase()
        for answer in answers:
            answer.from_user = answer.get_from_user()
            answer.content = utils.replace_at_html(answer.content)

            answer.is_request_user_like = (answer.id in request_user_like_answer_ids)   # 当前登录用户是否喜欢了改问题
            answer.is_request_user_bad = (answer.id in request_user_bads)   # 用户是否认为该问题无帮助
            if need_answer_likes:
                answer.likes = lb.format_likes(lb.get_likes_by_answer(answer)[:3])    # 赞了该回答的用户
        return answers

    @question_required
    @transaction.commit_manually(using=QUESTION_DB)
    def create_answer(self, question, from_user_id, content, ip=None):
        try:
            content = utils.filter_script(content)
            if not all((question, from_user_id, content)):
                transaction.rollback(using=QUESTION_DB)
                return 99800, dict_err.get(99800)

            errcode, errmsg = QuestionBase().validate_content(content)
            if not errcode == 0:
                transaction.rollback(using=QUESTION_DB)
                return errcode, errmsg

            to_user_id = question.user_id
            answer = Answer.objects.create(from_user_id=from_user_id, to_user_id=to_user_id, content=content,
                                           question=question, ip=ip)

            from_user = UserBase().get_user_by_id(from_user_id)
            # 添加at信息
            if content.find('@') != -1:
                at_usernicks = utils.select_at(content)
                for nick in at_usernicks:
                    at_user = UserBase().get_user_by_nick(nick)
                    if at_user:
                        # 自己@自己的关系不进行存储
                        if at_user.id != from_user_id:
                            AtAnswer.objects.create(answer=answer, user_id=at_user.id)
                            if at_user.id != to_user_id:
                                # 更新@未读消息数
                                UnreadCountBase().update_unread_count(at_user.id, code='at_answer')

                                # 发送提醒邮件
                                context = dict(user=from_user, answer=answer)
                                async_send_email(at_user.email, u'%s 在智选回答中@了你' % (from_user.nick, ), utils.render_email_template('email/at.html', context), 'html')

            # 更新未读消息
            if from_user_id != to_user_id:
                UnreadCountBase().update_unread_count(to_user_id, code='received_answer')

                # 发送提醒邮件
                to_user = UserBase().get_user_by_id(to_user_id)
                context = dict(user=from_user, answer=answer)
                async_send_email(to_user.email, u'%s 在智选回答了你的提问' % (from_user.nick, ), utils.render_email_template('email/answer.html', context), 'html')

            # 更新用户回答统计总数
            UserCountBase().update_user_count(user_id=from_user_id, code='user_answer_count')

            # 更新回答数冗余信息
            question.answer_count += 1
            question.last_answer_time = datetime.datetime.now()
            question.save()

            # 发送feed
            if not question.is_silence:
                FeedBase().create_feed(from_user_id, feed_type=3, obj_id=answer.id)

            # 更新summary
            QuestionBase().get_question_summary_by_id(question, must_update_cache=True)

            transaction.commit(using=QUESTION_DB)
            return 0, answer
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    @answer_admin_required
    def modify_answer(self, answer, user, content):
        try:
            content = utils.filter_script(content)
            if not content:
                return 99800, dict_err.get(99800)

            errcode, errmsg = QuestionBase().validate_content(content)
            if not errcode == 0:
                return errcode, errmsg

            answer.content = content
            answer.save()

            # 更新summary
            self.get_answer_summary_by_id(answer, must_update_cache=True)

            return 0, answer
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

    def get_answers_by_question_id(self, question_id):
        return Answer.objects.select_related('question').filter(question=question_id, state=True)

    def get_good_answers_by_question_id(self, question_id, sort=None):
        objs = Answer.objects.select_related('question').filter(question=question_id, state=True, is_bad=False)

        if sort:
            objs = objs.order_by(sort, 'id')
        else:
            objs = objs.order_by('id')
        return objs

    def get_bad_answers_by_question_id(self, question_id):
        return Answer.objects.select_related('question').filter(question=question_id, state=True, is_bad=True)

    def get_user_received_answer(self, user_id):
        return Answer.objects.select_related('question').filter(to_user_id=user_id, state=True)\
            .exclude(from_user_id=user_id).order_by('-id')

    def get_user_sended_answer(self, user_id):
        return Answer.objects.select_related('question').filter(from_user_id=user_id, state=True).order_by('-id')

    def get_at_answers(self, user_id):
        return [aa.answer for aa in AtAnswer.objects.select_related('answer', 'answer__question').filter(user_id=user_id)]

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
            UserCountBase().update_user_count(user_id=answer.from_user_id, code='user_answer_count', operate='minus')

            # 更新timeline
            FeedBase().remove_feed(answer.from_user_id, answer.id, feed_type=3)

            transaction.commit(using=QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    @answer_required
    @transaction.commit_manually(using=QUESTION_DB)
    def set_answer_bad(self, answer, user):
        try:
            if AnswerBad.objects.filter(answer=answer, user_id=user.id):
                transaction.rollback(using=QUESTION_DB)
                return 20106, dict_err.get(20106)

            AnswerBad.objects.create(answer=answer, user_id=user.id)
            if user.is_staff() or AnswerBad.objects.filter(answer=answer).count() >= 9:
                answer.is_bad = True
                answer.save()

            transaction.commit(using=QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    @answer_required
    @transaction.commit_manually(using=QUESTION_DB)
    def cancel_answer_bad(self, answer, user):
        try:
            AnswerBad.objects.filter(answer=answer, user_id=user.id).delete()
            if user.is_staff() or AnswerBad.objects.filter(answer=answer).count() <= 10:
                answer.is_bad = False
                answer.save()

            transaction.commit(using=QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)

    def get_answer_by_id(self, id, need_state=True):
        try:
            ps = dict(id=id)
            if need_state:
                ps.update(dict(state=True))
            return Answer.objects.select_related('question').get(**ps)
        except Answer.DoesNotExist:
            return None

    @cache_required(cache_key='answer_summary_%s', expire=3600)
    def get_answer_summary_by_id(self, answer_id_or_object, must_update_cache=False):
        '''
        @note: 获取回答摘要信息，用于feed展现
        '''
        answer = self.get_answer_by_id(answer_id_or_object, need_state=False) if not isinstance(answer_id_or_object, Answer) else answer_id_or_object
        answer_summary = {}
        if answer:
            user = answer.get_from_user()
            answer_summary = dict(answer_id=answer.id, question_id=answer.question.id, question_title=answer.question.title,
                                  answer_summary=answer.get_summary(), answer_like_count=answer.like_count, answer_user_id=user.id,
                                  answer_user_avatar=user.get_avatar_65(), answer_user_nick=user.nick, answer_user_des=user.des or '')
        return answer_summary

    def get_answers_by_range_date(self, start_date, end_date):
        '''
        查询指定区间的回答
        '''
        return Answer.objects.filter(create_time__range=(start_date, end_date))

    def search_answers(self, content):
        if not content:
            return []
        return Answer.objects.filter(content__icontains=content, state=True)[:200]


class LikeBase(object):

    '''
    @note: “喜欢”模块封装
    '''

    def format_likes(self, likes):
        for like in likes:
            like.from_user = UserBase().get_user_by_id(like.from_user_id)
        return likes

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
                    return 20104, dict_err.get(20104)
            else:
                from_user_id = ''
                is_anonymous = False
                if Like.objects.filter(ip=ip, answer=answer):
                    transaction.rollback(QUESTION_DB)
                    return 20104, dict_err.get(20104)

            # 不支持自赞
            to_user_id = answer.from_user_id
            if from_user_id == to_user_id:
                transaction.rollback(QUESTION_DB)
                return 20105, dict_err.get(20105)

            question = answer.question
            Like.objects.create(answer=answer, question=question, is_anonymous=is_anonymous,
                                from_user_id=from_user_id, to_user_id=to_user_id, ip=ip)
            answer.like_count += 1
            Answer.objects.filter(id=answer.id).update(like_count=F('like_count') + 1)

            # 更新被赞次数
            UserCountBase().update_user_count(user_id=to_user_id, code='user_liked_count')

            # 更新未读消息
            from www.message.interface import UnreadCountBase
            UnreadCountBase().update_unread_count(to_user_id, code='received_like')

            # 发送feed
            if not question.is_silence:
                FeedBase().create_feed(from_user_id, feed_type=2, obj_id=answer.id)

            # 更新summary
            AnswerBase().get_answer_summary_by_id(answer, must_update_cache=True)

            transaction.commit(QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(QUESTION_DB)
            return 99900, dict_err.get(99900)

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

    def get_likes_by_answer(self, answer):
        return Like.objects.select_related('answer').filter(answer=answer, is_anonymous=False)

    def get_user_liked_count(self, user_id):
        return self.get_to_user_likes(user_id).count()


class TopicBase(object):

    @cache_required(cache_key='all_topic', expire=0, cache_config=cache.CACHE_STATIC)
    def get_all_topics(self, must_update_cache=False):
        return Topic.objects.all()

    def get_topic_by_id_or_domain(self, topic_id_or_domain, need_state=True):
        topic_id_or_domain = str(topic_id_or_domain)
        for topic in self.get_all_topics():
            if topic.domain == topic_id_or_domain or str(topic.id) == topic_id_or_domain:
                if not(need_state and topic.state == 0):
                    return topic

    def get_topic_by_name(self, name, need_state=True):
        for topic in self.get_all_topics():
            if topic.name == name:
                if not(need_state and topic.state == 0):
                    return topic

    def get_topics_by_level(self, level):
        return [t for t in self.get_all_topics() if t.level == int(level) if t.state != 0]

    def get_all_question_type(self):
        '''
        @note: 获取所有一级话题，别名「话题类型」
        '''
        return self.get_topics_by_level(level=1)

    def get_all_topics_for_show(self):
        '''
        @note: 展示所有话题，目前展示二级话题
        '''
        return self.get_topics_by_level(level=2)

    def get_topics_by_parent(self, topic, need_state=True):
        '''
        @note: 获取所有子话题
        '''
        topic = topic if isinstance(topic, Topic) else self.get_topic_by_id_or_domain(topic)
        return [t for t in self.get_all_topics() if t.parent_topic_id == topic.id and not(need_state and t.state == 0)]

    def get_topic_all_parent(self, topic_id_or_object, include_self=True):
        '''
        @note: 获取话题所有的父话题
        '''
        topic = topic_id_or_object if isinstance(topic_id_or_object, Topic) else self.get_topic_by_id_or_domain(topic_id_or_object)
        parents = []
        topic.is_directly = True    # 提问和话题直接的对应关系
        i = 0
        while topic.domain != 'root':
            if not(i == 0 and include_self == False):
                parents.append(topic)
            topic = topic.parent_topic
            i += 1
        return parents

    def get_topic_level_by_parent(self, parent_topic):
        '''
        @note: 根据父话题获取提问等级
        '''
        parent_topic = parent_topic if isinstance(parent_topic, Topic) else self.get_topic_by_id_or_domain(parent_topic)
        return parent_topic.level + 1

    def get_topics_by_question(self, question, is_directly=True):
        return [tq.topic for tq in TopicQuestion.objects.select_related('topic').filter(question=question) if not(is_directly and not tq.is_directly)]

    @cache_required(cache_key='quesiton_type_%s', expire=3600 * 24)
    def get_topic_level1_by_question(self, question, must_update_cache=False):
        '''
        @note: 获取提问的类型，一级话题
        '''
        topics = [tq.topic for tq in TopicQuestion.objects.select_related('topic').filter(question=question) if tq.topic.level == 1]
        return topics[0] if topics else None

    def create_topic_question_relation(self, question, topic_ids, must_update=False):
        '''
        @note: 创建提问和话题的对应关系
        '''
        topics = [self.get_topic_by_id_or_domain(topic_id) for topic_id in topic_ids]
        topics = list(set(topics))

        topics_with_parent = []
        for topic_id in topic_ids:
            topics_with_parent.extend(self.get_topic_all_parent(topic_id))
        topics_with_parent = list(set(topics_with_parent))
        topics_exist = self.get_topics_by_question(question)

        # 删除后重建对应关系
        if set(topics) != set(topics_exist) or must_update:
            # 先更新话题数
            self.update_topic_question_count(question, operate="minus")
            TopicQuestion.objects.filter(question=question).delete()

            for topic in topics_with_parent:
                TopicQuestion.objects.create(topic=topic, question=question, is_directly=getattr(topic, 'is_directly', False))
                topic.question_count += 1
                topic.save()

            # 更新缓存
            self.get_topic_level1_by_question(question, must_update_cache=True)
            self.get_all_topics(must_update_cache=True)
        return True

    def update_topic_question_count(self, question, operate='minus'):
        '''
        @note: 更新话题提问数
        '''
        topics = self.get_topics_by_question(question)
        topics_with_parent = []
        for topic in topics:
            topics_with_parent.extend(self.get_topic_all_parent(topic))
        topics_with_parent = list(set(topics))
        for topic in topics_with_parent:
            if operate == 'minus':
                topic.question_count -= 1
            elif operate == 'add':
                topic.question_count += 1
            topic.save()

    def format_topics_for_ask_page(self, topics):
        ftopics = {}
        for topic in topics:
            if str(topic.parent_topic_id) not in ftopics:
                ftopics[str(topic.parent_topic_id)] = [(topic.id, topic.name), ]
            else:
                ftopics[str(topic.parent_topic_id)].append((topic.id, topic.name),)
        return ftopics

    def get_topics_by_name(self, topic_name):
        return Topic.objects.filter(name__contains=topic_name)

    def create_topic(self, name, domain, parent_topic_id, img, des, is_show=True, state=1):
        try:
            parent_topic = self.get_topic_by_id_or_domain(parent_topic_id)
            assert name and domain and parent_topic and des

            level = self.get_topic_level_by_parent(parent_topic)

            if self.get_topic_by_id_or_domain(domain, need_state=False) or self.get_topic_by_name(name, need_state=False):
                return 20107, dict_err.get(20107)

            topic = Topic.objects.create(name=name, domain=domain, parent_topic=parent_topic, level=level,
                                         img=img, des=des, state=state)
            parent_topic.child_count += 1
            parent_topic.save()

            # 更新缓存
            self.get_all_topics(must_update_cache=True)

            return 0, topic.id
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

    @transaction.commit_manually(using=QUESTION_DB)
    def modify_topic(self, topic_id, name, domain, des, img='', state=1, parent_topic_id=None, sort_num=0):
        try:
            topic = self.get_topic_by_id_or_domain(topic_id, need_state=False)
            if not (topic_id and name and domain and des):
                return 99800, dict_err.get(99800)

            if parent_topic_id:
                new_parent_topic = self.get_topic_by_id_or_domain(parent_topic_id)
                if new_parent_topic.level > topic.level:
                    return 20108, dict_err.get(20108)

                parent_topic = topic.parent_topic
                if parent_topic != new_parent_topic:
                    # 子话题数量更新
                    parent_topic.child_count -= 1
                    new_parent_topic.child_count += 1
                    parent_topic.save()
                    new_parent_topic.save()

                    for question in QuestionBase().get_questions_by_topic(topic):
                        # 删除旧的对应关系
                        for old_parent_topic_parent in self.get_topic_all_parent(parent_topic):
                            TopicQuestion.objects.filter(topic=old_parent_topic_parent, question=question).delete()
                            old_parent_topic_parent.question_count -= 1
                            old_parent_topic_parent.save()
                        # 建立新的对应关系
                        for new_parent_topic_parent in self.get_topic_all_parent(new_parent_topic):
                            TopicQuestion.objects.create(topic=new_parent_topic_parent, question=question)
                            new_parent_topic_parent.question_count += 1
                            new_parent_topic_parent.save()

                        # 更新缓存
                        self.get_topic_level1_by_question(question, must_update_cache=True)

            # 判断名称和domain是否重复
            exist_topic = self.get_topic_by_id_or_domain(domain, need_state=False)
            if exist_topic and topic != exist_topic:
                return 20107, dict_err.get(20107)
            exist_topic = self.get_topic_by_name(name, need_state=False)
            if exist_topic and topic != exist_topic:
                return 20107, dict_err.get(20107)

            topic.name = name
            topic.domain = domain
            topic.img = img
            topic.des = des
            topic.sort_num = sort_num
            if parent_topic_id:
                topic.parent_topic = new_parent_topic
                topic.level = self.get_topic_level_by_parent(new_parent_topic)

            state = int(state)
            if topic.state != state:
                # 修改状态的时候更新父话题的子话题数
                if state == 0:
                    parent_topic.child_count -= 1
                elif state in (1, 2) and topic.state == 0:
                    parent_topic.child_count += 1
                parent_topic.save()

            topic.state = state
            topic.save()

            # 更新缓存
            self.get_all_topics(must_update_cache=True)
            transaction.commit(using=QUESTION_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=QUESTION_DB)
            return 99900, dict_err.get(99900)
