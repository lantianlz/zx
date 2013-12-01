# -*- coding: utf-8 -*-


class UserBase(object):

    def __init__(self):
        from common import password_hashers
        self.hasher = password_hashers.MD5PasswordHasher()

    def set_password(self, raw_password):
        self.password = self.hasher.make_password(raw_password)
        return self.password

    def check_password(self, raw_password):
        return self.hasher.check_password(raw_password, self.password)

    # 注册

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
