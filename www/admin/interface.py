# -*- coding: utf-8 -*-

from django.db.models import Count
from django.db import transaction

from www.misc import consts

from admin.models import Permission, UserPermission
from account.interface import UserBase

dict_err = {}

dict_err.update(consts.G_DICT_ERROR)


class PermissionBase(object):

    """docstring for PermissionBase"""

    def __init__(self):
        pass

    def get_all_permissions(self):
        '''
        获取所有权限
        '''
        return [x for x in Permission.objects.filter(parent__isnull=True)]

    def get_user_permissions(self, user_id):
        '''
        根据用户id 获取此用户所有权限
        '''
        return [x.permission.code for x in UserPermission.objects.select_related('permission').filter(user_id=user_id)]

    def get_all_administrators(self):
        '''
        获取所有管理员
        '''
        user_ids = [x['user_id'] for x in UserPermission.objects.values('user_id').annotate(dcount=Count('user_id'))]

        return [UserBase().get_user_by_id(x) for x in user_ids]

    @transaction.commit_manually
    def save_user_permission(self, user_id, permissions, creator):
        '''
        修改用户权限
        '''

        if not user_id or not permissions or not creator:
            return 99800, dict_err.get(99800)

        try:
            UserPermission.objects.filter(user_id=user_id).delete()

            for x in permissions:
                UserPermission.objects.create(user_id=user_id, permission_id=x, creator=creator)

            transaction.commit()
        except Exception, e:
            print e
            transaction.rollback()
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def cancel_admin(self, user_id):
        '''
        取消管理员
        '''

        if not user_id:
            return 99800, dict_err.get(99800)

        UserPermission.objects.filter(user_id=user_id).delete()

        return 0, dict_err.get(0)
