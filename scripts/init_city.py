# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


import json
from pprint import pprint

city_data = open('./kaihu/city.txt').read()
city_data = json.loads(city_data)['province']


def get_province_type(province):
    if province in (u'北京市', u'上海市', u'天津市', u'重庆市'):
        return 2
    if u'自治区' in province:
        return 1
    return 0


def get_city_by_province(province):
    for cd in city_data:
        if cd['name'] == province:
            return cd['city']
    raise Exception, (u'can not find city: %s' % province).encode('utf8')


def get_city_pinyin(city_name):
    return {
        u'海南藏族自治州': u'hnczzz1',
        u'海南其他': u'hnqt2',
        u'伊春市': u'yichun1',
        u'榆林市': u'yulin1',
        u'抚州市': u'fuzhou1',
        u'宿州市': u'suzhou1',
        u'台州市': u'taizho1',
        u'重庆市': u'chongqing',

    }.get(city_name)


def init_city():
    from common.pinyin import pinyin
    from django.db.utils import IntegrityError
    from www.kaihu.models import City

    dict_areas = {
        u'华北地区': (10, [u'北京市', u'天津市', u'河北省', u'山西省', u'内蒙古自治区']),
        u'东北地区': (9, [u'辽宁省', u'吉林省', u'黑龙江省']),
        u'华东地区': (8, [u'上海市', u'江苏省', u'浙江省', u'安徽省', u'福建省', u'江西省', u'山东省']),
        u'华中地区': (7, [u'河南省', u'湖北省', u'湖南省']),
        u'华南地区': (6, [u'广东省', u'广西壮族自治区', u'海南省']),
        u'西南地区': (5, [u'重庆市', u'四川省', u'贵州省', u'云南省', u'西藏自治区']),
        u'西北地区': (4, [u'陕西省', u'甘肃省', u'青海省', u'宁夏回族自治区', u'新疆维吾尔自治区']),
    }
    pinyin = pinyin.Pinyin()
    lst_pinyin = []
    lst_pinyin_abbr = []
    for area in dict_areas:
        area = City.objects.create(area=area, location_type=0, sort_num=dict_areas[area][0])
        provinces = dict_areas[area.area][1]
        for province in provinces:
            province_name = province
            province = City.objects.create(area=area.id, province=province, location_type=1, province_type=get_province_type(province))
            citys = get_city_by_province(province_name)
            for city in citys:
                city_name = city['name']
                if city_name == u'市辖区':
                    city_name = province_name   # 直辖市特殊处理
                if city_name == u'县':
                    continue

                # 检测拼音是否重复
                city_pinyin = get_city_pinyin(city_name) or pinyin.get_pinyin(city_name[:-1])   # 重复的特殊处理
                city_pinyin_abbr = pinyin.get_initials(city_name[:-1])
                if city_pinyin in lst_pinyin:
                    print u'拼音重名'.encode('utf8'), city_pinyin, city_name.encode('utf8')
                if city_pinyin_abbr in lst_pinyin_abbr:
                    # print u'缩写重名'.encode('utf8'), city_pinyin_abbr, city_name.encode('utf8')
                    city_pinyin_abbr = city_pinyin

                if not city_pinyin in lst_pinyin:
                    lst_pinyin.append(city_pinyin)
                if not city_pinyin_abbr in lst_pinyin_abbr:
                    lst_pinyin_abbr.append(city_pinyin_abbr)
                # continue

                city_obj = City.objects.create(area=area.id, province=province.id, city=city_name, location_type=2, pinyin=city_pinyin, pinyin_abbr=city_pinyin_abbr)

                districts = city['area']
                for district in districts:
                    if district['name'] == u'市辖区':
                        continue
                    City.objects.create(area=area.id, province=province.id, city=city_obj.id, location_type=3, district=district['name'])

    print 'ok'


if __name__ == '__main__':
    init_city()
