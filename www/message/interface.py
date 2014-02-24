# -*- coding: utf-8 -*-

import datetime
import logging
import json
from django.db import transaction

from common import utils, debug, cache
from www.message.models import UnreadCount, UnreadType


dict_err = {
    100: u'',

    998: u'参数缺失',
    999: u'系统错误',
    000: u'成功'
}


class UnreadCountBase(object):

    """
    @note: 封装未读数信息操作类
    """

    def __init__(self):
        self.cache_obj = cache.Cache(config=cache.CACHE_TMP)

    def __del__(self):
        del self.cache_obj

    def get_notification_type(self):
        """
        @note: 获取提醒类型数据
        """
        cache_key = u'notification_type_all'
        cache_obj = cache.Cache(config=cache.CACHE_STATIC)

        if cache_obj.exists(cache_key):
            nts = cache_obj.get(cache_key)
        else:
            nts = UnreadType.objects.all().order_by('type', 'id')
            cache_obj.set(cache_key, nts)
        return nts

    def get_or_create_count_info(self, user):
        """
        @note: 获取用户未读数对象
        """
        user_id = utils.get_uid(user)
        obj_urcs = UnreadCount.objects.filter(user_id=user_id)
        created = True
        if not obj_urcs:
            count_info = self.init_count_info()
            urc = UnreadCount.objects.create(user_id=user_id, count_info=count_info)
            created = False
        else:
            urc = obj_urcs[0]
        return urc, created

    def init_count_info(self):
        """
        @note: 获取初始未读数信息
        """

        nts = self.get_notification_type()
        count_info = {}
        for nt in nts:
            count_info.setdefault(str(nt.code), 0)
        return json.dumps(count_info)

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
        cache_key = u'%s_%s' % ('notification', user_id)
        self.cache_obj.set(cache_key, count_info, 3600 * 24)

        return True

    def get_unread_count(self, user):
        """
        @note: 获取未读数
        """

        user_id = utils.get_uid(user)
        cache_key = u'%s_%s' % ('notification', user_id)
        # 从缓存中取
        if self.cache_obj.exists(cache_key):
            count_info = self.cache_obj.get(cache_key)
        # 从数据库中取
        else:
            try:
                count_info = UnreadCount.objects.get(user_id=user_id).count_info
            except UnreadCount.DoesNotExist:
                count_info = self.init_count_info()  # 没有就不用自动创建，更新的时候进行创建
            self.cache_obj.set(cache_key, json.loads(count_info), 3600 * 24)
        return count_info

    def get_unread_count_total(self, user):
        count_info = self.get_unread_count(user)
        return sum(count_info.values())

    def clear_count_info_by_code(self, code, user_id):
        """
        @note: 通用的清除消息数的方法，数字大于0的才去调用清除，提高效率
        """
        if code and user_id and int(UnreadCountBase().get_unread_count(user_id).get(code, 0)) > 0:
            UnreadCountBase().update_unread_count(user_id, code, operate='clear')
