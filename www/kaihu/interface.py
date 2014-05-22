# -*- coding: utf-8 -*-

import json

from common import utils, cache
from www.misc.decorators import cache_required
from www.misc import consts
from www.kaihu.models import Company, Department, City


dict_err = {
    50100: u'',
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
