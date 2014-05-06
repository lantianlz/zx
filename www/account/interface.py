# -*- coding: utf-8 -*-

import datetime
import time
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache
from www.account.models import User, Profile, ExternalToken, Invitation, InvitationUser, UserCount
from www.message.interface import UnreadCountBase

dict_err = {
    100: u'邮箱重复',
    101: u'昵称重复',
    102: u'手机号重复',
    103: u'被逮到了，无效的性别值',
    104: u'这么奇葩的生日怎么可能',
    105: u'两次输入密码不相同',
    106: u'当前密码错误',
    107: u'新密码和老密码不能相同',
    108: u'登陆密码验证失败',
    109: u'新邮箱和老邮箱不能相同',
    110: u'邮箱验证码错误或者已过期，请重新验证',
    111: u'该邮箱尚未注册',
    112: u'code已失效，请重新执行重置密码操作',

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
        assert raw_password
        self.password = self.hasher.make_password(raw_password)
        return self.password

    def check_password(self, raw_password, password):
        return self.hasher.check_password(raw_password, getattr(self, 'password', password))

    def set_profile_login_att(self, profile, user):
        for key in ['email', 'mobilenumber', 'username', 'last_login', 'password', 'state']:
            setattr(profile, key, getattr(user, key))
        # profile.is_staff = lambda:user.is_staff()
        setattr(profile, 'user_login', user)

    def get_user_login_by_id(self, id):
        try:
            user = User.objects.get(id=id, state__gt=0)
            return user
        except User.DoesNotExist:
            return None

    def get_user_by_id(self, id):
        try:
            profile = Profile.objects.get(id=id)
            user = User.objects.get(id=profile.id, state__gt=0)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_nick(self, nick):
        try:
            profile = Profile.objects.get(nick=nick)
            user = User.objects.get(id=profile.id, state__gt=0)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_email(self, email):
        try:
            user = User.objects.get(email=email, state__gt=0)
            profile = Profile.objects.get(id=user.id)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_mobilenumber(self, mobilenumber):
        try:
            if mobilenumber:
                user = User.objects.get(mobilenumber=mobilenumber, state__gt=0)
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

    def check_gender(self, gender):
        if not str(gender) in ('0', '1', '2'):
            return False, dict_err.get(103)
        return True, dict_err.get(000)

    def check_birthday(self, birthday):
        try:
            birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')
            now = datetime.datetime.now()
            assert (now + datetime.timedelta(days=100 * 365)) > birthday > (now - datetime.timedelta(days=100 * 365))
        except:
            return False, dict_err.get(104)
        return True, dict_err.get(000)

    @transaction.commit_manually(using=ACCOUNT_DB)
    def regist_user(self, email, nick, password, ip, mobilenumber=None, username=None,
                    source=0, gender=0, invitation_code=None):
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

            user = User.objects.create(id=id, email=email, mobilenumber=mobilenumber, last_login=now,
                                       password=self.set_password(password)
                                       )
            profile = Profile.objects.create(id=id, nick=nick, ip=ip, source=source, gender=gender)
            self.set_profile_login_att(profile, user)

            if invitation_code:
                invitation = InvitationBase().add_invitation_user(invitation_code, profile.id)
                if invitation:
                    # 发送系统通知
                    content = u'成功邀请一个注册用户 <a href="%s">%s</a>' % (profile.get_url(), profile.nick)
                    UnreadCountBase().add_system_message(user_id=invitation.user_id, content=content)

            transaction.commit(using=ACCOUNT_DB)

            # todo发送验证邮件
            return True, profile
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=ACCOUNT_DB)
            return False, dict_err.get(999)

    def get_user_by_external_info(self, source, access_token, external_user_id,
                                  refresh_token, nick, ip, expire_time,
                                  user_url='', gender=0):
        assert all((source, access_token, external_user_id, nick))
        et = self.get_external_user(source, access_token, external_user_id, refresh_token)
        if et:
            return True, self.get_user_by_id(et.user_id)
        else:
            email = '%s@mrzhixuan.com' % (int(time.time() * 1000), )
            nick = self.generate_nick_by_external_nick(nick)
            if not nick:
                return False, u'生成名称异常'
            expire_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time()) + int(expire_time)))
            flag, result = self.regist_user(email=email, nick=nick, password=email, ip=ip, source=1, gender=gender)
            if flag:
                user = result
                ExternalToken.objects.create(source=source, external_user_id=external_user_id,
                                             access_token=access_token, refresh_token=refresh_token, user_url=user_url,
                                             nick=nick, user_id=user.id, expire_time=expire_time
                                             )
                return True, user
            else:
                return False, result

    def generate_nick_by_external_nick(self, nick):
        if not self.get_user_by_nick(nick):
            return nick
        else:
            for i in xrange(3):
                new_nick = '%s_%s' % (nick, i)
                if not self.get_user_by_nick(new_nick):
                    return new_nick
            for i in xrange(10):
                return '%s_%s' % (nick,  str(int(time.time() * 1000))[-3:])

    def get_external_user(self, source, access_token, external_user_id, refresh_token):
        assert all((source, access_token, external_user_id))

        et = None
        ets = list(ExternalToken.objects.filter(source=source, external_user_id=external_user_id))
        if ets:
            et = ets[0]
            if et.access_token != access_token:
                et.access_token = access_token
                et.refresh_token = refresh_token
                et.save()
        else:
            ets = list(ExternalToken.objects.filter(source=source, access_token=access_token))
            if ets:
                et = ets[0]
                if et.external_user_id != external_user_id:
                    et.external_user_id = external_user_id
                    et.refresh_token = refresh_token
                    et.save()
        return et

    def change_profile(self, user, nick, gender, birthday, des=None):
        '''
        @note: 资料修改
        '''
        user_id = user.id
        if not (user_id and nick and gender and birthday):
            return False, dict_err.get(998)

        try:
            validators.vnick(nick)
        except Exception, e:
            return False, smart_unicode(e)

        if user.nick != nick and self.get_user_by_nick(nick):
            return False, dict_err.get(101)

        flag, result = self.check_gender(gender)
        if not flag:
            return flag, result

        flag, result = self.check_birthday(birthday)
        if not flag:
            return flag, result

        user = self.get_user_by_id(user_id)
        user.nick = nick
        user.gender = int(gender)
        user.birthday = birthday
        if des:
            user.des = utils.filter_script(des)[:128]
        user.save()

        # todo:触发事件，比如清除缓存等
        return True, user

    def change_pwd(self, user, old_password, new_password_1, new_password_2):
        '''
        @note: 密码修改
        '''
        if not all((old_password, new_password_1, new_password_2)):
            return False, dict_err.get(998)

        if new_password_1 != new_password_2:
            return False, dict_err.get(105)
        if not self.check_password(old_password, user.password):
            return False, dict_err.get(106)
        if old_password == new_password_1:
            return False, dict_err.get(107)
        try:
            validators.vpassword(new_password_1)
        except Exception, e:
            return False, smart_unicode(e)

        user_login = self.get_user_login_by_id(user.id)
        user_login.password = self.set_password(new_password_1)
        user_login.save()
        return True, dict_err.get(000)

    def change_email(self, user, email, password):
        '''
        @note: 邮箱修改
        '''
        if not all((email, password)):
            return False, dict_err.get(998)

        if not self.check_password(password, user.password):
            return False, dict_err.get(108)

        if user.email == email:
            return False, dict_err.get(109)

        try:
            validators.vemail(email)
        except Exception, e:
            return False, smart_unicode(e)

        if user.email != email and self.get_user_by_email(email):
            return False, dict_err.get(100)

        user_login = self.get_user_login_by_id(user.id)
        user_login.email = email
        user_login.save()

        # todo发送验证邮件
        return True, dict_err.get(000)

    def send_confirm_email(self, user):
        '''
        @note: 发送验证邮件
        '''
        cache_obj = cache.Cache()
        key = u'confirm_email_code_%s' % user.id
        code = cache_obj.get(key)
        if not code:
            code = utils.uuid_without_dash()
            cache_obj.set(key, code, time_out=1800)

        if not cache_obj.get_time_is_locked(key, 60):
            from www.tasks import async_send_email

            context = {'verify_url': '%s/account/user_settings/verify_email?code=%s' % (settings.MAIN_DOMAIN, code), }

            async_send_email(user.email, u'智选邮箱验证',
                             utils.render_email_template('email/verify_email.html', context), 'html')

    def check_email_confim_code(self, user, code):
        '''
        @note: 确认邮箱
        '''
        if not code:
            return False, dict_err.get(998)

        cache_obj = cache.Cache()
        key = u'confirm_email_code_%s' % user.id
        cache_code = cache_obj.get(key)

        if cache_code != code:
            return False, dict_err.get(110)

        user.email_verified = True
        user.save()
        return True, user

    def send_forget_password_email(self, email):
        '''
        @note: 发送密码找回邮件
        '''
        if not email:
            return False, dict_err.get(998)

        user = self.get_user_by_email(email)
        if not user:
            return False, dict_err.get(111)
        cache_obj = cache.Cache()
        key = u'forget_password_email_code_%s' % email
        code = cache_obj.get(key)
        if not code:
            code = utils.uuid_without_dash()
            cache_obj.set(key, code, time_out=1800)
            cache_obj.set(code, user, time_out=1800)

        if not cache_obj.get_time_is_locked(key, 60):
            from www.tasks import async_send_email

            context = {
                'reset_url': '%s/reset_password?code=%s' % (settings.MAIN_DOMAIN, code),
            }

            async_send_email(email, u'智选找回密码',
                             utils.render_email_template('email/reset_password.html', context), 'html')
        return True, dict_err.get(000)

    def get_user_by_code(self, code):
        cache_obj = cache.Cache()
        return cache_obj.get(code)

    def reset_password_by_code(self, code, new_password_1, new_password_2):
        user = self.get_user_by_code(code)
        if not user:
            return False, dict_err.get(112)

        if new_password_1 != new_password_2:
            return False, dict_err.get(105)
        try:
            validators.vpassword(new_password_1)
        except Exception, e:
            return False, smart_unicode(e)

        user_login = self.get_user_login_by_id(user.id)
        user_login.password = self.set_password(new_password_1)
        user_login.save()

        cache_obj = cache.Cache()
        key = u'forget_password_email_code_%s' % user.email
        cache_obj.delete(key)
        cache_obj.delete(code)
        return True, user_login


class InvitationBase(object):

    def format_invitation_user(self, invitation_users):
        for iu in invitation_users:
            iu.user = UserBase().get_user_by_id(iu.user_id)
        return invitation_users

    def get_invitation_by_user_id(self, user_id):
        try:
            invitation = Invitation.objects.create(user_id=user_id, code=utils.get_random_code())
        except:
            invitation = Invitation.objects.get(user_id=user_id)
        return invitation

    def get_invitation_by_code(self, code):
        try:
            return Invitation.objects.get(code=code)
        except Invitation.DoesNotExist:
            return None

    def add_invitation_user(self, code, user_id):
        invitation = self.get_invitation_by_code(code)
        try:
            InvitationUser.objects.create(user_id=user_id, invitation=invitation)
        except:
            pass
        return invitation

    def get_invitation_user(self, user_id):
        return InvitationUser.objects.select_related('invitation').filter(invitation__user_id=user_id)


def user_profile_required(func):
    '''
    @note: 访问用户控件装饰器
    '''
    def _decorator(request, user_id, *args, **kwargs):
        from www.timeline.interface import UserFollowBase
        from django.http import HttpResponse

        ufb = UserFollowBase()
        ub = UserBase()
        if not user_id:
            user = request.user
        else:
            user = ub.get_user_by_id(user_id)
            if not user:
                err_msg = u'用户不存在'
                return HttpResponse(err_msg)
        request.is_me = (request.user == user)
        if not request.is_me:
            request.is_follow = ufb.check_is_follow(request.user.id, user.id)

        user_count_info = UserCountBase().get_user_count_info(user_id)
        request.user_question_count = user_count_info['user_question_count']
        request.user_answer_count = user_count_info['user_answer_count']
        request.user_liked_count = user_count_info['user_liked_count']
        request.following_count = user_count_info['following_count']
        request.follower_count = user_count_info['follower_count']

        return func(request, user, *args, **kwargs)
    return _decorator


class UserCountBase(object):

    def __init__(self):
        pass

    def get_user_count_info(self, user_id):
        try:
            uc = UserCount.objects.get(user_id=user_id)
            return dict(user_question_count=uc.user_question_count, user_answer_count=uc.user_answer_count,
                        user_liked_count=uc.user_liked_count, following_count=uc.following_count,
                        follower_count=uc.follower_count)
        except UserCount.DoesNotExist:
            return dict(user_question_count=0, user_answer_count=0, user_liked_count=0,
                        following_count=0, follower_count=0)

    def update_user_count(self, user_id, code, operate="add"):
        assert (user_id and code)
        uc, created = UserCount.objects.get_or_create(user_id=user_id)
        count = getattr(uc, code)
        if operate == 'add':
            count += 1
        else:
            count -= 1
        setattr(uc, code, count)
        uc.save()
