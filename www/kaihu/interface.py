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

    def get_all_city_group_by_province(self):
        data = []
        areas = self.get_all_areas()
        provinces = City.objects.filter(location_type=1)
        citys = City.objects.filter(location_type=2)

        for area in areas:
            area_provices = provinces.filter(area=area.id)
            data_citys = []
            for ap in area_provices:
                province_citys = citys.filter(province=ap.id)
                data_citys.append([ap, province_citys])
            data.append([area, data_citys])
        return data
