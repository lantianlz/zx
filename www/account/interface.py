# -*- coding: utf-8 -*-

import datetime
import time
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache
# from www.misc.decorators import cache_required
from www.misc import consts
from www.account.models import User, Profile, ExternalToken, Invitation, InvitationUser, UserCount
from www.account.models import RecommendUser, LastActive
from www.message.interface import UnreadCountBase

dict_err = {
    10100: u'邮箱重复',
    10101: u'昵称重复',
    10102: u'手机号重复',
    10103: u'被逮到了，无效的性别值',
    10104: u'这么奇葩的生日怎么可能',
    10105: u'两次输入密码不相同',
    10106: u'当前密码错误',
    10107: u'新密码和老密码不能相同',
    10108: u'登陆密码验证失败',
    10109: u'新邮箱和老邮箱不能相同',
    10110: u'邮箱验证码错误或者已过期，请重新验证',
    10111: u'该邮箱尚未注册',
    10112: u'code已失效，请重新执行重置密码操作',
    10113: u'没有找到对象',
}
dict_err.update(consts.G_DICT_ERROR)

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

    def get_user_by_id(self, id, state=[1, 2]):
        try:
            profile = Profile.objects.get(id=id)
            user = User.objects.get(id=profile.id, state__in=state)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_nick(self, nick, state=[1, 2]):
        try:
            profile = Profile.objects.get(nick=nick)
            user = User.objects.get(id=profile.id, state__in=state)
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
            return 10100, dict_err.get(10100)
        if self.get_user_by_nick(nick):
            return 10101, dict_err.get(10101)
        if self.get_user_by_mobilenumber(mobilenumber):
            return 10102, dict_err.get(10102)
        return 0, dict_err.get(0)

    def check_gender(self, gender):
        if not str(gender) in ('0', '1', '2'):
            return 10103, dict_err.get(10103)
        return 0, dict_err.get(0)

    def check_birthday(self, birthday):
        try:
            birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')
            now = datetime.datetime.now()
            assert (now + datetime.timedelta(days=100 * 365)) > birthday > (now - datetime.timedelta(days=100 * 365))
        except:
            return 10104, dict_err.get(10104)
        return 0, dict_err.get(0)

    @transaction.commit_manually(using=ACCOUNT_DB)
    def regist_user(self, email, nick, password, ip, mobilenumber=None, username=None,
                    source=0, gender=0, invitation_code=None):
        '''
        @note: 注册
        '''
        try:
            if not (email and nick and password):
                transaction.rollback(using=ACCOUNT_DB)
                return 99800, dict_err.get(99800)

            errcode, errmsg = self.check_user_info(email, nick, password, mobilenumber)
            if errcode != 0:
                transaction.rollback(using=ACCOUNT_DB)
                return errcode, errmsg

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

                    # 自动关注邀请者
                    from www.timeline.interface import UserFollowBase
                    UserFollowBase().follow_people(profile.id, invitation.user_id)

            transaction.commit(using=ACCOUNT_DB)

            # todo发送验证邮件
            return 0, profile
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=ACCOUNT_DB)
            return 99900, dict_err.get(99900)

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
            errcode, result = self.regist_user(email=email, nick=nick, password=email, ip=ip, source=1, gender=gender)
            if errcode == 0:
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
            return 99800, dict_err.get(99800)

        try:
            validators.vnick(nick)
        except Exception, e:
            return 99900, smart_unicode(e)

        if user.nick != nick and self.get_user_by_nick(nick):
            return 10101, dict_err.get(10101)

        errcode, errmsg = self.check_gender(gender)
        if errcode != 0:
            return errcode, errmsg

        errcode, errmsg = self.check_birthday(birthday)
        if errcode != 0:
            return errcode, errmsg

        user = self.get_user_by_id(user_id)
        user.nick = nick
        user.gender = int(gender)
        user.birthday = birthday
        if des:
            user.des = utils.filter_script(des)[:128]
        user.save()

        # todo:触发事件，比如清除缓存等
        return 0, user

    def change_pwd(self, user, old_password, new_password_1, new_password_2):
        '''
        @note: 密码修改
        '''
        if not all((old_password, new_password_1, new_password_2)):
            return 99800, dict_err.get(99800)

        if new_password_1 != new_password_2:
            return 10105, dict_err.get(10105)
        if not self.check_password(old_password, user.password):
            return 10106, dict_err.get(10106)
        if old_password == new_password_1:
            return 10107, dict_err.get(10107)
        try:
            validators.vpassword(new_password_1)
        except Exception, e:
            return 99900, smart_unicode(e)

        user_login = self.get_user_login_by_id(user.id)
        user_login.password = self.set_password(new_password_1)
        user_login.save()
        return 0, dict_err.get(0)

    def change_email(self, user, email, password):
        '''
        @note: 邮箱修改
        '''
        if not all((email, password)):
            return 99800, dict_err.get(99800)

        if not self.check_password(password, user.password):
            return 10108, dict_err.get(10108)

        if user.email == email:
            return 10109, dict_err.get(10109)

        try:
            validators.vemail(email)
        except Exception, e:
            return 99900, smart_unicode(e)

        if user.email != email and self.get_user_by_email(email):
            return 10100, dict_err.get(10100)

        user_login = self.get_user_login_by_id(user.id)
        user_login.email = email
        user_login.save()

        # todo发送验证邮件
        return 0, dict_err.get(0)

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
            return 99800, dict_err.get(99800)

        cache_obj = cache.Cache()
        key = u'confirm_email_code_%s' % user.id
        cache_code = cache_obj.get(key)

        if cache_code != code:
            return 10110, dict_err.get(10110)

        user.email_verified = True
        user.save()
        return 0, user

    def send_forget_password_email(self, email):
        '''
        @note: 发送密码找回邮件
        '''
        if not email:
            return 99800, dict_err.get(99800)

        user = self.get_user_by_email(email)
        if not user:
            return 10111, dict_err.get(10111)
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
        return 0, dict_err.get(0)

    def get_user_by_code(self, code):
        cache_obj = cache.Cache()
        return cache_obj.get(code)

    def reset_password_by_code(self, code, new_password_1, new_password_2):
        user = self.get_user_by_code(code)
        if not user:
            return 10112, dict_err.get(10112)

        if new_password_1 != new_password_2:
            return 10105, dict_err.get(10105)
        try:
            validators.vpassword(new_password_1)
        except Exception, e:
            return 99900, smart_unicode(e)

        user_login = self.get_user_login_by_id(user.id)
        user_login.password = self.set_password(new_password_1)
        user_login.save()

        cache_obj = cache.Cache()
        key = u'forget_password_email_code_%s' % user.email
        cache_obj.delete(key)
        cache_obj.delete(code)
        return 0, user_login

    def update_user_last_active_time(self, user_id, ip=None, last_active_source=0):
        '''
        @note: 更新用户最后活跃时间
        '''
        cache_obj = cache.Cache()
        # 一小时更新一次
        if not cache_obj.get_time_is_locked(key=u'last_active_time_%s' % user_id, time_out=3600):
            try:
                la = LastActive.objects.get(user_id=user_id)
                la.ip = ip
                la.last_active_source = last_active_source
                la.last_active_time = datetime.datetime.now()
                la.save()
            except LastActive.DoesNotExist:
                LastActive.objects.create(user_id=user_id, last_active_time=datetime.datetime.now(),
                                          ip=ip, last_active_source=last_active_source)

    def get_all_users(self):
        '''
        '''
        return User.objects.all()

    def format_user_full_info(self, user_id):
        '''
        格式化完整用户信息
        '''
        format_user = self.get_user_by_id(user_id)
        # 判断是否已经是推荐用户了
        if RecommendUser.objects.filter(user_id=user_id).count() > 0:
            format_user.is_recommend = True
        else:
            format_user.is_recommend = False

        # 统计信息
        format_user.user_count = UserCountBase().get_user_count_info(user_id)

        # 是否管理员
        from www.admin.interface import PermissionBase
        if PermissionBase().get_user_permissions(user_id):
            format_user.is_admin = True
        else:
            format_user.is_admin = False

        # 客户经理
        from www.kaihu.interface import CustomerManagerBase
        if CustomerManagerBase().get_customer_manager_by_user_id(user_id):
            format_user.is_customer_manager = True
        else:
            format_user.is_customer_manager = False

        # 活跃时间
        la = LastActive.objects.filter(user_id=user_id)
        if la:
            la = la[0]
            format_user.last_active = la.last_active_time
        else:
            format_user.last_active = format_user.create_time

        return format_user

    def get_active_users(self, date):

        return LastActive.objects.filter(last_active_time__gte=date)


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


class RecommendUserBase(object):

    def __init__(self):
        pass

    def format_recommend_user(self, recommend_users):
        '''
        格式化
        '''
        for recommend_user in recommend_users:
            recommend_user.user = UserBase().get_user_by_id(recommend_user.user_id)
            recommend_user.user_count = UserCountBase().get_user_count_info(recommend_user.user_id)

        return recommend_users

    # @cache_required(cache_key='recommend_user_%s', expire=3600)
    def get_recommend_users(self, user_id, random=False):
        from www.timeline.interface import UserFollowBase
        exclude_user_ids = [f.to_user_id for f in UserFollowBase().get_following_by_user_id(user_id)]
        exclude_user_ids.append(user_id)
        if not random:
            rusers = RecommendUser.objects.exclude(user_id__in=exclude_user_ids)
        else:
            rusers = RecommendUser.objects.exclude(user_id__in=exclude_user_ids).order_by('?')
        return rusers[:4]

    def get_all_recommend_users(self):
        '''
        获取所有的推荐用户信息(admin)
        '''

        return self.format_recommend_user(RecommendUser.objects.all())

    def set_recommend_user_sort(self, user_id, sort_num):
        '''
        设置推荐用户排序

        user_id: 用户id
        sort_num: 排序数值
        '''
        if not user_id or not sort_num:
            return 99800, dict_err.get(99800)

        recommend_user = RecommendUser.objects.filter(user_id=user_id)
        if recommend_user:
            try:
                recommend_user = recommend_user[0]
                recommend_user.sort_num = sort_num
                recommend_user.save()
                return 0, dict_err.get(0)
            except Exception, e:
                debug.get_debug_detail(e)
                return 99900, smart_unicode(e)

        return 10113, dict_err.get(10113)

    def un_recommend_user(self, user_id):
        '''
        取消推荐用户设置

        user_id: 用户id
        '''
        if not user_id:
            return 99800, dict_err.get(99800)

        recommend_user = RecommendUser.objects.filter(user_id=user_id)
        if recommend_user:
            try:
                recommend_user = recommend_user[0]
                recommend_user.delete()
                return 0, dict_err.get(0)
            except Exception, e:
                debug.get_debug_detail(e)
                return 99900, smart_unicode(e)

        return 10113, dict_err.get(10113)

    def set_recommend_user(self, user_id):
        '''
        设置推荐用户

        user_id: 用户id
        '''
        if not user_id:
            return 99800, dict_err.get(99800)

        recommend_user = RecommendUser.objects.filter(user_id=user_id)
        if not recommend_user:
            try:
                RecommendUser.objects.create(user_id=user_id)
                return 0, dict_err.get(0)
            except Exception, e:
                debug.get_debug_detail(e)
                return 99900, smart_unicode(e)

        return 10113, dict_err.get(10113)

    def get_user_by_nick(self, user_nick):
        '''
        '''
        if not user_nick:
            return None

        user = UserBase().get_user_by_nick(user_nick)

        if user:
            # 判断是否已经是推荐用户了
            if RecommendUser.objects.filter(user_id=user.id).count() > 0:
                user.is_recommend = True
            else:
                user.is_recommend = False

            # 补充统计信息
            user.user_count = UserCountBase().get_user_count_info(user.id)
            return user

        return None
