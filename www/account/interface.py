# -*- coding: utf-8 -*-

import datetime
from django.db import transaction

from common import utils
from www.account.models import User, Profile


dict_err = {
    100: u'',

    999: u'系统错误',
    000: u'成功'
}


class UserBase(object):

    def __init__(self):
        from common import password_hashers
        self.hasher = password_hashers.MD5PasswordHasher()

    def set_password(self, raw_password):
        self.password = self.hasher.make_password(raw_password)
        return self.password

    def check_password(self, raw_password):
        return self.hasher.check_password(raw_password, self.password)

    @transaction.commit_manually()
    def regist_user(self, email, nick, password, ip, mobilenumber=None, username=None):
        '''
        @note: 注册
        '''
        try:
            id = utils.uuid_without_dash()
            now = datetime.datetime.now()

            user = User.objects.create(id=id, email=email, mobilenumber=mobilenumber,
                                       username=username, password=self.set_password(password),
                                       last_login=now, create_time=now)
            profile = Profile.objects.create(id=id, nick=nick, ip=ip)

            transaction.commit()
            return user, profile
        except Exception, e:
            transaction.rollback()
            return dict_err.get(999)



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
