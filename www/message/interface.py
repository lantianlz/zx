# -*- coding: utf-8 -*-

import json
from django.db import transaction

from common import utils, cache, debug
from www.misc.decorators import cache_required
from www.misc import consts
from www.tasks import async_send_email
from www.account.interface import UserBase
from www.message.models import UnreadCount, UnreadType, Notice, InviteAnswer, InviteAnswerIndex, GlobalNotice


dict_err = {
    40100: u'自己不能邀请自己哦',
    40101: u'最多邀请6人',
    40102: u'已邀请，请勿重复邀请',
    40103: u'没有找到对应的通知'
}
dict_err.update(consts.G_DICT_ERROR)

DEFAULT_DB = 'default'


class UnreadCountBase(object):

    """
    @note: 封装未读数信息操作类
    """

    def __init__(self):
        self.cache_obj = cache.Cache(config=cache.CACHE_TMP)

    def __del__(self):
        del self.cache_obj

    @cache_required(cache_key='unread_type_all', expire=0, cache_config=cache.CACHE_STATIC)
    def get_unread_type(self, must_update_cache=False):
        """
        @note: 获取提醒类型数据
        """
        return UnreadType.objects.all().order_by('type', 'id')

    def get_or_create_count_info(self, user):
        """
        @note: 获取用户未读数对象
        """
        user_id = utils.get_uid(user)
        obj_urcs = UnreadCount.objects.filter(user_id=user_id)
        created = True
        if not obj_urcs:
            count_info = self.init_count_info()
            urc = UnreadCount.objects.create(user_id=user_id, count_info=json.dumps(count_info))
            created = False
        else:
            urc = obj_urcs[0]
        return urc, created

    def init_count_info(self):
        """
        @note: 获取初始未读数信息
        """

        nts = self.get_unread_type()
        count_info = {}
        for nt in nts:
            count_info.setdefault(str(nt.code), 0)
        return count_info

    def update_unread_count(self, user, code, operate="add"):
        """
        @note: 更新提醒未读数
        """

        if UnreadType.objects.filter(code=code).count() == 0:
            return False

        urc, created = self.get_or_create_count_info(user)
        count_info = json.loads(urc.count_info)

        if not count_info.has_key(code):
            count_info.setdefault(code, 0)
        # 加一或者重置
        if operate == 'add':
            count_info[code] += 1
        else:
            count_info[code] = 0

        urc.count_info = json.dumps(count_info)
        urc.save()
        # 操作缓存
        user_id = utils.get_uid(user)
        cache_key = u'%s_%s' % ('unread_count', user_id)
        self.cache_obj.set(cache_key, count_info, 3600 * 24)

        return True

    @cache_required(cache_key='unread_count_%s', expire=3600 * 24)
    def get_unread_count_info(self, user):
        """
        @note: 获取未读数
        """
        user_id = utils.get_uid(user)
        try:
            count_info = json.loads(UnreadCount.objects.get(user_id=user_id).count_info)
        except UnreadCount.DoesNotExist:
            count_info = self.init_count_info()  # 没有就不用自动创建，更新的时候进行创建
        return count_info

    def get_unread_count_total(self, user):
        count_info = self.get_unread_count_info(user)
        return count_info

    def clear_count_info_by_code(self, user_id, code):
        """
        @note: 通用的清除消息数的方法，数字大于0的才去调用清除，提高效率
        """
        if code and user_id and int(UnreadCountBase().get_unread_count_info(user_id).get(code, 0)) > 0:
            UnreadCountBase().update_unread_count(user_id, code, operate='clear')

    def get_system_message(self, user_id):
        return Notice.objects.filter(user_id=user_id)

    def add_system_message(self, user_id, content, source=0):
        notice = Notice.objects.create(user_id=user_id, content=content, source=source)
        UnreadCountBase().update_unread_count(user_id, code='system_message')
        return notice

    def send_system_message_to_staffs(self, content):
        """
        @note: 给所有内部成员发送通知
        """
        for user in UserBase().get_all_staffs():
            self.add_system_message(user.id, content)


class InviteAnswerBase(object):

    def __init__(self):
        pass

    def format_invite_user(self, show_invite_users, invited_users):
        from www.custom_tags.templatetags.custom_filters import str_display

        show_invite_users_json = []
        invited_users_json = []
        invited_user_ids = [iu.to_user_id for iu in invited_users]

        for siu in show_invite_users:
            user = UserBase().get_user_by_id(siu.user_id)
            show_invite_users_json.append(dict(user_id=user.id, user_nick=user.nick, user_avatar=user.get_avatar_65(), gender=user.gender,
                                               user_des=str_display((user.des or '').strip(), 17), is_invited=siu.user_id in invited_user_ids))
        for iu in invited_users:
            invited_users_json.append(dict(user_id=iu.to_user_id, user_nick=UserBase().get_user_by_id(iu.to_user_id).nick))
        return show_invite_users_json, invited_users_json

    def format_user_received_invites(self, user_received_invites):
        from www.question.interface import QuestionBase

        ub = UserBase()
        for uri in user_received_invites:
            uri.question = QuestionBase().get_question_summary_by_id(uri.question_id)
            uri.from_users = [ub.get_user_by_id(user_id) for user_id in json.loads(uri.from_user_ids)]
            uri.from_users.reverse()
        return user_received_invites

    @transaction.commit_manually(using=DEFAULT_DB)
    def create_invite(self, from_user_id, to_user_id, question_id):
        try:
            from www.question.interface import QuestionBase

            ub = UserBase()
            try:
                from_user = ub.get_user_by_id(from_user_id)
                to_user = ub.get_user_by_id(to_user_id)
                question = QuestionBase().get_question_by_id(question_id)

                assert from_user and to_user and question
            except:
                transaction.rollback(using=DEFAULT_DB)
                return 99800, dict_err.get(99800)

            if from_user_id == to_user_id:
                transaction.rollback(using=DEFAULT_DB)
                return 40100, dict_err.get(40100)

            # 同一个问题最多邀请6个人
            if InviteAnswerIndex.objects.filter(from_user_id=from_user_id, question_id=question_id).count() >= 6:
                transaction.rollback(using=DEFAULT_DB)
                return 40101, dict_err.get(40101)

            # 重复邀请给出提示
            if InviteAnswerIndex.objects.filter(from_user_id=from_user_id, to_user_id=to_user_id, question_id=question_id):
                transaction.rollback(using=DEFAULT_DB)
                return 40102, dict_err.get(40102)

            try:
                ia = InviteAnswer.objects.create(from_user_ids=json.dumps([from_user_id, ]), to_user_id=to_user_id, question_id=question_id)
                need_update_unread_count = True
            except:
                ia = InviteAnswer.objects.get(to_user_id=to_user_id, question_id=question_id)
                from_user_ids = json.loads(ia.from_user_ids)
                if from_user_id not in from_user_ids:
                    from_user_ids.append(from_user_id)
                ia.from_user_ids = json.dumps(from_user_ids)
                ia.save()

                need_update_unread_count = True if ia.is_read else False

            # 建立索引
            InviteAnswerIndex.objects.create(from_user_id=from_user_id, to_user_id=to_user_id, question_id=question_id)

            # 更新未读消息，新邀请或者邀请已读才更新未读数
            if need_update_unread_count:
                UnreadCountBase().update_unread_count(to_user_id, code='invite_answer')

            # 发送提醒邮件
            context = dict(user=from_user, question=question)
            async_send_email(to_user.email, u'%s 在智选邀请你回答问题' % (from_user.nick, ), utils.render_email_template('email/invite.html', context), 'html')

            transaction.commit(using=DEFAULT_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def get_user_received_invite(self, to_user_id):
        return InviteAnswer.objects.filter(to_user_id=to_user_id)

    def get_invited_user_by_question_id(self, from_user_id, question_id):
        return InviteAnswerIndex.objects.filter(from_user_id=from_user_id, question_id=question_id)

    def update_invite_is_read(self, to_user_id):
        return InviteAnswer.objects.filter(to_user_id=to_user_id).update(is_read=True)


class GlobalNoticeBase(object):

    def __init__(self):
        pass

    def format_global_notice(self, objs):
        data = []
        for obj in objs:
            data.append(dict(notice_id=obj.id, content=obj.content, level=obj.level))
        return data

    def create_global_notice(self, content, start_time, end_time, user_id, level=0, platform=0):
        try:
            assert content and start_time and end_time
            assert end_time > start_time
        except:
            return 99800, dict_err.get(99800)

        obj = GlobalNotice.objects.create(content=content, start_time=start_time, end_time=end_time,
                                          user_id=user_id, level=level, platform=platform)

        self.get_all_valid_global_notice(must_update_cache=True)
        return 0, obj.id

    @cache_required(cache_key='get_all_valid_global_notice', expire=3600)
    def get_all_valid_global_notice(self, must_update_cache=False):
        import datetime
        now = datetime.datetime.now()
        return GlobalNotice.objects.filter(end_time__gt=now, start_time__lt=now)

    def get_all_global_notice(self):
        return GlobalNotice.objects.all()

    def get_notice_by_id(self, notice_id):
        if not notice_id:
            return None

        obj = GlobalNotice.objects.filter(id=notice_id)
        if not obj:
            return None

        return obj[0]

    def modify_global_notice(self, notice_id, **kwargs):
        try:
            assert kwargs.get('content') and kwargs.get('start_time') and kwargs.get('end_time')
            assert kwargs.get('end_time') > kwargs.get('start_time')
        except:
            return 99800, dict_err.get(99800)

        if not notice_id:
            return 40103, dict_err.get(40103)

        obj = GlobalNotice.objects.filter(id=notice_id)
        if not obj:
            return 40103, dict_err.get(40103)

        obj = obj[0]
        try:
            for k, v in kwargs.items():
                setattr(obj, k, v)

            obj.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        # 更新缓存
        self.get_all_valid_global_notice(must_update_cache=True)
        return 0, dict_err.get(0)

    def remove_global_notice(self, notice_id):
        if not notice_id:
            return 40103, dict_err.get(40103)

        obj = GlobalNotice.objects.filter(id=notice_id)
        if not obj:
            return 40103, dict_err.get(40103)

        obj.delete()

        # 更新缓存
        self.get_all_valid_global_notice(must_update_cache=True)
        return 0, dict_err.get(0)
