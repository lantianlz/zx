# -*- coding: utf-8 -*-

from www.account.interface import UserBase


def _save(*argv, **kwargs):
    pass


class AuthBackend(object):
    supports_inactive_user = True

    def authenticate(self, username=None, password=None):
        ub = UserBase()
        user = ub.get_user_by_email(username)
        if not user:
            user = ub.get_user_by_mobilenumber(username)
        if user and ub.check_password(password, user.password):
            # todo 更新最后登录时间
            user.save = _save
            return user

    def get_user(self, user_id):
        print '============>', user_id
        user = UserBase().get_user_by_id(user_id)
        if user:
            setattr(user, "is_authenticated", lambda: True)
            setattr(user, "is_active", True)
        return user
