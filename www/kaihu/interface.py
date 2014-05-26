# -*- coding: utf-8 -*-

import datetime

from common import cache, debug
from www.misc.decorators import cache_required
from www.misc import consts
from www.account.interface import UserBase, UserCountBase
from www.kaihu.models import Company, Department, City, CustomerManager, FriendlyLink


dict_err = {
    50100: u'找不到指定用户',
    50101: u'找不到指定营业部',
    50102: u'找不到指定客户经理',
}
dict_err.update(consts.G_DICT_ERROR)


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
            obj.department = DepartmentBase().get_department_by_id(obj.department.id)
        return objs

    def add_customer_manager(self, user_id, department_id_or_obj, end_date, vip_info='', sort_num=0, qq=None, entry_time=None, mobile=None,
                             real_name=None, id_card=None, id_cert=None, des=None):
        if not (user_id and department_id_or_obj and end_date):
            return 99800, dict_err.get(99800)

        user = UserBase().get_user_by_id(user_id)
        if not user:
            return 50100, dict_err.get(50100)

        department = department_id_or_obj if isinstance(department_id_or_obj, Department) else DepartmentBase().get_department_by_id(department_id_or_obj)
        if not department:
            return 50101, dict_err.get(50101)

        try:
            CustomerManager.objects.create(user_id=user_id, department=department, end_date=end_date, sort_num=sort_num, city_id=department.city_id,
                                           qq=qq, entry_time=entry_time, mobile=mobile, vip_info=vip_info,
                                           real_name=real_name, id_card=id_card, id_cert=id_cert, des=des)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

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
        return CustomerManager.objects.filter(city_id=city_id, end_date__gte=datetime.datetime.now(), state=True)

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

    def remove_customer_manager(self, user_id):
        obj = self.get_customer_manager_by_user_id(user_id)
        if obj:
            obj.delete()
            return 0, dict_err.get(0)

        return 50100, dict_err.get(50100)


class FriendlyLinkBase(object):

    def __init__(self):
        pass

    def add_friendly_link(self, name, href, link_type=0, city_id=None, img=None, sort_num=0):
        try:
            try:
                assert name and href
                if link_type == 0:
                    assert city_id
            except:
                return 99800, dict_err.get(99800)
            FriendlyLink.objects.create(name=name, href=href, city_id=city_id, img=img, link_type=link_type, sort_num=sort_num)

            # 更新缓存
            self.get_all_friendly_link(must_update_cache=True)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)
        return 0, dict_err.get(0)

    @cache_required(cache_key='all_friendly_link', expire=0, cache_config=cache.CACHE_STATIC)
    def get_all_friendly_link(self, must_update_cache=False):
        return FriendlyLink.objects.filter(state=True)

    def get_friendly_link_by_city_id(self, city_id, link_type=(0, )):
        flinks = []
        for flink in (self.get_all_friendly_link()):
            if flink.city_id == city_id and flink.link_type in link_type:
                flinks.append(flink)
        return flinks

    def get_friendly_link_by_link_type(self, link_type):
        flinks = []
        link_type = link_type if isinstance(link_type, (list, tuple)) else (link_type,)
        for flink in (self.get_all_friendly_link()):
            if flink.link_type in link_type:
                flinks.append(flink)
        return flinks
