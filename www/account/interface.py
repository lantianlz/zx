# -*- coding: utf-8 -*-

import datetime
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators
from www.account.models import User, Profile


dict_err = {
    100: u'邮箱重复',
    101: u'昵称重复',
    102: u'手机号重复',

    998: u'参数缺失',
    999: u'系统错误',
    000: u'成功'
}
ACCOUNT_DB = settings.ACCOUNT_DB


class UserBase(object):

    def __init__(self):
        from common import password_hashers
        self.hasher = password_hashers.MD5PasswordHasher()

    def set_password(self, raw_password):
        self.password = self.hasher.make_password(raw_password)
        return self.password

    def check_password(self, raw_password, password):
        return self.hasher.check_password(raw_password, getattr(self, 'password', password))

    def set_profile_login_att(self, profile, user):
        for key in ['email', 'mobilenumber', 'username', 'last_login', 'password']:
            setattr(profile, key, getattr(user, key))

    def get_user_by_id(self, id):
        try:
            profile = Profile.objects.get(id=id)
            user = User.objects.get(id=profile.id)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_nick(self, nick):
        try:
            profile = Profile.objects.get(nick=nick)
            user = User.objects.get(id=profile.id)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_email(self, email):
        try:
            user = User.objects.get(email=email)
            profile = Profile.objects.get(id=user.id)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_mobilenumber(self, mobilenumber):
        try:
            user = User.objects.get(mobilenumber=mobilenumber)
            profile = Profile.objects.get(id=user.id)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def check_user_info(self, email, nick, password, mobilenumber):
        try:
            validators.vemail(email)
            validators.vnick(nick)
            validators.vpassword(password)
        except Exception, e:
            return False, smart_unicode(e)

        if self.get_user_by_email(email):
            return False, dict_err.get(100)
        if self.get_user_by_nick(nick):
            return False, dict_err.get(101)
        if self.get_user_by_mobilenumber(mobilenumber):
            return False, dict_err.get(102)
        return True, dict_err.get(000)

    @transaction.commit_manually(using=ACCOUNT_DB)
    def regist_user(self, email, nick, password, ip, mobilenumber=None, username=None):
        '''
        @note: 注册
        '''
        try:
            if not (email and nick and password):
                transaction.rollback(using=ACCOUNT_DB)
                return False, dict_err.get(998)

            flag, result = self.check_user_info(email, nick, password, mobilenumber)
            if not flag:
                transaction.rollback(using=ACCOUNT_DB)
                return flag, result

            id = utils.uuid_without_dash()
            now = datetime.datetime.now()

            user = User.objects.create(id=id, email=email, mobilenumber=mobilenumber,
                                       password=self.set_password(password),
                                       last_login=now, create_time=now)
            profile = Profile.objects.create(id=id, nick=nick, ip=ip, create_time=now)
            transaction.commit(using=ACCOUNT_DB)

            # 发送验证邮件和通知邮件
            # 其他触发事件
            self.set_profile_login_att(profile, user)
            return True, profile
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=ACCOUNT_DB)
            return False, dict_err.get(999)



    # 生成验证码

    # 发送验证邮件

    # 确认邮箱

    # 登陆

    # 注销

    # 密码修改

    # 忘记密码

    # 邮箱修改

    # 资料修改

    # 获取用户
