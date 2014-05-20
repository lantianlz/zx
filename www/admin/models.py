# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.conf import settings


class Permission(models.Model):

    '''
    权限类 
    '''
    name = models.CharField(verbose_name=u'权限名称', max_length=64)
    code = models.CharField(verbose_name=u'权限代码', max_length=32, unique=True)
    parent = models.ForeignKey('self', verbose_name=u'父权限', related_name="children", null=True)

    def __unicode__(self):
        return '%s-%s' % (self.name, self.code)


class UserPermission(models.Model):

    '''
    用户权限表
    '''
    user_id = models.CharField(verbose_name=u'用户', max_length=32)
    permission = models.ForeignKey(Permission, verbose_name=u'权限')
    create_time = models.DateTimeField(verbose_name=u'创建时间', db_index=True, default=datetime.datetime.now)
    creator = models.CharField(verbose_name=u'创建者', max_length=32)
