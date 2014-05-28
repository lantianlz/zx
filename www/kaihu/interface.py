# -*- coding: utf-8 -*-

import datetime
from django.db import transaction

from common import cache, debug
from www.misc.decorators import cache_required
from www.misc import consts
from www.account.interface import UserBase, UserCountBase
from www.kaihu.models import Company, Department, City, CustomerManager, FriendlyLink


dict_err = {
    50100: u'找不到指定用户',
    50101: u'找不到指定营业部',
    50102: u'找不到指定客户经理',
    50103: u'找不到指定友情链接',
}
dict_err.update(consts.G_DICT_ERROR)

KAIHU_DB = 'kaihu'


class CityBase(object):

    def __init__(self):
        pass

    def get_all_areas(self):
        return City.objects.filter(location_type=0)

    def get_all_citys(self):
        return City.objects.filter(location_type=2)

    def get_all_city_group_by_province(self):
        data = []
        areas = self.get_all_areas()
        provinces = City.objects.filter(location_type=1)
        citys = self.get_all_citys()

        for area in areas:
            area_provices = provinces.filter(area=area.id)
            data_citys = []
            for ap in area_provices:
                province_citys = citys.filter(province=ap.id)
                data_citys.append([ap, province_citys])
            data.append([area, data_citys])
        return data

    def get_city_by_pinyin_abbr(self, pinyin_abbr):
        if pinyin_abbr:
            citys = self.get_all_citys().filter(pinyin_abbr=pinyin_abbr)
            if citys:
                return citys[0]

    def get_city_by_id(self, city_id):
        if city_id:
            citys = self.get_all_citys().filter(id=city_id)
            if citys:
                return citys[0]

    def get_citys_by_name(self, city_name):
        citys = []

        if city_name:
            citys = self.get_all_citys().filter(city__contains=city_name)

        return citys

    def get_one_city_by_name(self, city_name):
        objs = self.get_all_citys().filter(city=city_name)
        if objs:
            return objs[0]
        return None


class DepartmentBase(object):

    def __init__(self):
        pass

    def get_all_departments(self):
        return Department.objects.select_related('company').all()

    def get_departments_by_city_id(self, city_id):
        return list(self.get_all_departments().filter(city_id=city_id))

    def get_department_by_id(self, department_id):
        try:
            department = self.get_all_departments().filter(id=department_id)[0]
            department.city = CityBase().get_city_by_id(department.city_id)
        except Exception:
            department = None
        return department

    def get_departments_by_name(self, department_name):
        departments = []
        if department_name:
            departments = self.get_all_departments().filter(name__contains=department_name)
        return departments


class CustomerManagerBase(object):

    def __init__(self):
        pass

    def format_customer_managers(self, objs):
        for obj in objs:
            obj.user = UserBase().get_user_by_id(obj.user_id)
            obj.user.user_count_info = UserCountBase().get_user_count_info(obj.user_id)
            obj.department = DepartmentBase().get_department_by_id(obj.department.id)   # 得到city信息
        return objs

    def format_customer_managers_for_ajax(self, objs):
        data = []
        for obj in objs:
            user = UserBase().get_user_by_id(obj.user_id)
            user_count_info = UserCountBase().get_user_count_info(obj.user_id)
            data.append(dict(user_id=user.id, user_nick=user.nick, user_avatar=user.get_avatar_65(),
                             department_name=obj.department.get_short_name(), company_short_name=obj.department.company.get_short_name(),
                             department_id=obj.department.id, city_id=obj.city_id,
                             sort_num=obj.sort_num, vip_info=obj.vip_info, qq=obj.qq, mobile=obj.mobile, pay_type=obj.pay_type,
                             user_question_count=user_count_info['user_question_count'], user_answer_count=user_count_info['user_answer_count'],
                             user_liked_count=user_count_info['user_liked_count'],
                             ))
        return data

    @transaction.commit_manually(using=KAIHU_DB)
    def add_customer_manager(self, user_id, department_id_or_obj, end_date, vip_info='', sort_num=0, qq=None, entry_time=None, mobile=None,
                             real_name=None, id_card=None, id_cert=None, des=None):
        try:
            if not (user_id and department_id_or_obj and end_date):
                return 99800, dict_err.get(99800)

            user = UserBase().get_user_by_id(user_id)
            if not user:
                return 50100, dict_err.get(50100)

            department = department_id_or_obj if isinstance(department_id_or_obj, Department) else DepartmentBase().get_department_by_id(department_id_or_obj)
            if not department:
                return 50101, dict_err.get(50101)

            CustomerManager.objects.create(user_id=user_id, department=department, end_date=end_date, sort_num=sort_num, city_id=department.city_id,
                                           qq=qq, entry_time=entry_time, mobile=mobile, vip_info=vip_info,
                                           real_name=real_name, id_card=id_card, id_cert=id_cert, des=des)

            # 更新营业部冗余字段
            department.cm_count += 1
            department.save()

            transaction.commit(using=KAIHU_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=KAIHU_DB)
            return 99900, dict_err.get(99900)

    def modify_customer_manager(self, user_id, **kwargs):
        if not user_id:
            return 99800, dict_err.get(99800)

        user = UserBase().get_user_by_id(user_id)
        if not user:
            return 50100, dict_err.get(50100)

        customer_manager = self.get_customer_manager_by_user_id(user_id)
        if not customer_manager:
            return 50102, dict_err.get(50102)

        # 如果修改了营业部，所属城市也要一并修改
        department_id = kwargs.get('department_id')
        if department_id:
            temp = DepartmentBase().get_department_by_id(department_id)
            if not temp:
                return 50101, dict_err.get(50101)
            else:
                kwargs.update({'city_id': temp.city_id})

        try:
            for k, v in kwargs.items():
                setattr(customer_manager, k, v)

            customer_manager.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_customer_managers_by_city_id(self, city_id):
        cms = list(CustomerManager.objects.select_related('department').filter(city_id=city_id, end_date__gte=datetime.datetime.now(), state=True))
        cms = self.format_customer_managers_for_ajax(cms)

        # 排序方法，按照两个维度，付费类型和赞
        def _cmp(x, y):
            return - 1 if (x['pay_type'] > y['pay_type'] or (x['pay_type'] == y['pay_type'] and x['user_liked_count'] > y['user_liked_count'])) else 1
        cms.sort(cmp=_cmp)
        return cms

    def get_customer_managers_by_department(self, department):
        return CustomerManager.objects.filter(department=department, state=True)

    def get_customer_manager_by_user_id(self, user_id):
        obj = CustomerManager.objects.filter(user_id=user_id)
        if obj:
            return obj[0]
        else:
            return None

    def get_all_customer_managers(self, active=True, state=True):
        objs = CustomerManager.objects.all()
        if active:
            objs = objs.filter(end_date__gte=datetime.datetime.now())

        if state != None:
            objs = objs.filter(state=state)

        return objs

    @transaction.commit_manually(using=KAIHU_DB)
    def remove_customer_manager(self, user_id):
        try:
            obj = self.get_customer_manager_by_user_id(user_id)
            if obj:
                obj.delete()

                # 更新营业部冗余字段
                department = obj.department
                department.cm_count -= 1
                department.save()

                transaction.commit(using=KAIHU_DB)
                return 0, dict_err.get(0)
            else:
                transaction.commit(using=KAIHU_DB)
                return 50100, dict_err.get(50100)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=KAIHU_DB)
            return 99900, dict_err.get(99900)


class FriendlyLinkBase(object):

    def __init__(self):
        pass

    def format_friendly_links(self, friendly_links):
        cb = CityBase()

        for x in friendly_links:
            x.city = cb.get_city_by_id(x.city_id)

        return friendly_links

    def add_friendly_link(self, name, href, link_type=0, city_id=None, img=None, des=None, sort_num=0):
        try:
            try:
                assert name and href
                if link_type == 0:
                    assert city_id
            except:
                return 99800, dict_err.get(99800)
            obj = FriendlyLink.objects.create(name=name, href=href, city_id=city_id, img=img, link_type=link_type, sort_num=sort_num, des=des)

            # 更新缓存
            self.get_all_friendly_link(must_update_cache=True)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)
        return 0, obj.id

    @cache_required(cache_key='all_friendly_link', expire=0, cache_config=cache.CACHE_STATIC)
    def get_all_friendly_link(self, state=True, must_update_cache=False):
        objects = FriendlyLink.objects.all()
        if state != None:
            objects = objects.filter(state=state)

        return objects

    def get_friendly_link_by_city_id(self, city_id, link_type=(0, )):
        flinks = []
        for flink in (self.get_all_friendly_link()):
            if flink.city_id == city_id and flink.link_type in link_type:
                flinks.append(flink)
        return flinks

    def get_friendly_link_by_id(self, link_id, state=True):
        return self.get_all_friendly_link(state).filter(id=link_id)

    def get_friendly_link_by_name(self, link_name):
        return self.get_all_friendly_link(state=None).filter(name=link_name)

    def get_friendly_link_by_link_type(self, link_type):
        flinks = []
        link_type = link_type if isinstance(link_type, (list, tuple)) else (link_type,)
        for flink in (self.get_all_friendly_link()):
            if flink.link_type in link_type:
                flinks.append(flink)
        return flinks

    def modify_friendly_link(self, link_id, **kwargs):
        if not link_id:
            return 99800, dict_err.get(99800)

        friendly_link = self.get_friendly_link_by_id(link_id, state=None)
        if not friendly_link:
            return 50103, dict_err.get(50103)

        friendly_link = friendly_link[0]

        try:
            for k, v in kwargs.items():
                setattr(friendly_link, k, v)

            friendly_link.save()

            # 更新缓存
            self.get_all_friendly_link(must_update_cache=True)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def remove_friendly_link(self, link_id):
        if not link_id:
            return 99800, dict_err.get(99800)

        friendly_link = self.get_friendly_link_by_id(link_id, state=None)
        if not friendly_link:
            return 50103, dict_err.get(50103)
        friendly_link = friendly_link[0]
        friendly_link.delete()

        self.get_all_friendly_link(must_update_cache=True)
        return 0, dict_err.get(0)
