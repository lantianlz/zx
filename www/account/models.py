# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.conf import settings

from www.account import const


class User(models.Model):

    '''
    用户类
    '''
    state_choices = (
        (const.INVALID_USER, u'无效用户'),
        (const.VALID_USER, u'有效用户'),
        (const.INTERNAL_MEMBER, u'内部成员'),
    )

    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=32, unique=True)
    email = models.CharField(verbose_name=u'邮箱', max_length=64, unique=True)
    mobilenumber = models.CharField(verbose_name=u'邮箱', max_length=32, null=True, unique=True)
    username = models.CharField(verbose_name=u'用户名', max_length=32, null=True, unique=True)
    password = models.CharField(verbose_name=u'密码', max_length=128)
    state = models.IntegerField(verbose_name=u'用户状态', default=1, choices=state_choices, db_index=True)
    last_login = models.DateTimeField(verbose_name=u'上次登陆时间', db_index=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', db_index=True, default=datetime.datetime.now)

    def is_staff(self):
        return self.state in (const.INTERNAL_MEMBER, )

    def __unicode__(self):
        return '%s, %s' % (self.id, self.email)


class Profile(models.Model):

    '''
    用户扩展信息
    '''
    gender_choices = (
        (const.UNKNOWN, u'未设置'),
        (const.MALE, u'男'),
        (const.FEMALE, u'女'),
    )
    source_choices = ((0, u'web'), (1, u'weibo'))

    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=32, unique=True)
    nick = models.CharField(max_length=32, unique=True)
    domain = models.CharField(max_length=32, unique=True, null=True)
    birthday = models.DateField(default='2000-01-01', db_index=True)
    gender = models.IntegerField(verbose_name=u'性别', default=0, choices=gender_choices, db_index=True)
    avatar = models.CharField(verbose_name=u'头像', max_length=256, default='')
    email_verified = models.BooleanField(verbose_name=u'邮箱是否验证过', default=False)
    mobile_verified = models.BooleanField(verbose_name=u'手机是否验证过', default=False)
    ip = models.CharField(verbose_name=u'登陆ip', max_length=32, null=True)
    des = models.CharField(max_length=256, null=True)
    source = models.IntegerField(default=0, choices=source_choices)
    create_time = models.DateTimeField(verbose_name=u'创建时间', db_index=True, default=datetime.datetime.now)

    def is_staff(self):
        # 从user移植过来避免cPickle的dumps报错
        return self.state in (const.INTERNAL_MEMBER, )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_url(self):
        return u'/p/%s' % self.id

    def get_avatar(self, key=''):
        if self.avatar:
            return '%s%s' % (self.avatar, ('!%s' % key) if key else '')
        else:
            return '%s/img/common/default.png' % settings.MEDIA_URL

    def get_avatar_600(self):
        return self.get_avatar(key='600m0')

    def get_avatar_300(self):
        return self.get_avatar(key='300m300')

    def get_avatar_100(self):
        return self.get_avatar(key='100m100')

    def get_avatar_65(self):
        return self.get_avatar(key='65m65')

    def get_avatar_25(self):
        return self.get_avatar(key='25m25')

    def get_ta_display(self):
        return {1: u'他'}.get(self.gender, u'她')

    def __unicode__(self):
        return u'%s, %s' % (self.id, self.nick)


class UserChangeLog(models.Model):
    change_type_choices = (
        (const.PASSWORD, u'密码'),
        (const.EMAIL, u'邮箱'),
        (const.MOBILE, u'手机'),
    )

    change_type = models.IntegerField(verbose_name=u'变更类型', choices=change_type_choices)
    befor = models.CharField(verbose_name=u'变更前', max_length=64, db_index=True)
    after = models.CharField(max_length=64, db_index=True, verbose_name=u'变更后')
    ip = models.CharField(verbose_name=u'操作ip', max_length=32, null=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', db_index=True, default=datetime.datetime.now)


class LastActive(models.Model):
    pass


class ExternalToken(models.Model):
    user_id = models.CharField(max_length=32, db_index=True)
    source = models.CharField(max_length=16, db_index=True)
    access_token = models.CharField(max_length=128, db_index=True)
    external_user_id = models.CharField(max_length=64, db_index=True)
    refresh_token = models.CharField(max_length=128, db_index=True)
    nick = models.CharField(max_length=64, null=True)
    user_url = models.CharField(max_length=128, null=True)
    expire_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    state = models.BooleanField(default=True)

    class Meta:
        unique_together = [("source", "access_token"), ("source", "external_user_id")]


class Invitation(models.Model):
    user_id = models.CharField(max_length=32, unique=True)
    code = models.CharField(max_length=32, unique=True)

    def get_url(self):
        from django.conf import settings
        return u'%s/regist/%s' % (settings.MAIN_DOMAIN, self.code)

    def get_user(self):
        from www.account.interface import UserBase
        user = UserBase().get_user_by_id(self.user_id)
        return user


class InvitationUser(models.Model):
    user_id = models.CharField(max_length=32, db_index=True)
    invitation = models.ForeignKey('Invitation')
    state = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user_id', 'invitation')]
        ordering = ["-id"]


class BlackList(models.Model):
    type_choices = ((0, u'全部'), (1, u'禁止登陆'), (2, u'禁止发帖'))
    user_id = models.CharField(max_length=32, db_index=True)
    type = models.IntegerField(default=0, choices=type_choices)
    state = models.BooleanField(default=True)
    expire_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
