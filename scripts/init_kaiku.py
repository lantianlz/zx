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
from django.conf import settings
from www.misc import qiniu_client
from www.kaihu.models import Company, Department, City

dict_zip_code = {}
lst_miss_zip_code = []


def init_city_zip_code():
    global dict_zip_code
    for line in open('./kaihu/zip_code.txt'):
        line = unicode(line.strip(), 'utf8')
        if line:
            data = line.split('=')
            # print line.encode('utf8')
            dict_zip_code[data[1]] = data[0]

    dict_zip_code_3 = {}
    dict_zip_code_4 = {}
    for key in dict_zip_code:
        dict_zip_code_4[key[:4]] = dict_zip_code[key]
        dict_zip_code_3[key[:3]] = dict_zip_code[key]

    dict_zip_code = dict_zip_code_3
    # pprint(dict_zip_code)


def get_city_name_by_zip_code(zip_code):
    if zip_code[:2] in ('10', '20', '30', '40',):
        return dict_zip_code[zip_code[:2]]
    try:
        return dict_zip_code[zip_code[:3]]
    except:
        lst_miss_zip_code.append([zip_code, Department.objects.filter(zip_code=zip_code)[0].addr.encode('utf8')])


def init_kaihu_info():
    from django.db.utils import IntegrityError

    data = open('./kaihu/quanshang.txt').read()
    data = json.loads(data)
    departments = data['result']

    cs = []
    ds = []
    cnames = []
    # dnames = {}
    for d in departments:
        if d['FULL_NAME'] not in cnames:
            cnames.append(d['FULL_NAME'])
            cs.append(dict(unique_id=d['BROKERAGEFIRM'], name=d['FULL_NAME']))

        ds.append(dict(unique_id=d['BRANCH_UNIQUE_ID'],
                  addr=d['ADDR'],
                  c_unique_id=d['BROKERAGEFIRM'],
                  assess_date=d['ASSESS_DATE'],
                  tel=d['EXTERNAL_TEL'],
                  zip_code=d['ZIP_CODE'],
                  licence=d['LICENCE'],
                  manager_name=d['MANAGER'],
                  name=d['BRANCHNAME']))

    cobjs_by_id = {}
    if False:
        # 创建证券公司信息
        for c in cs:
            try:
                company = Company.objects.create(**c)
            except:
                company = Company.objects.get(unique_id=c['unique_id'])
            cobjs_by_id[c['unique_id']] = company

        # 创建营业部信息
        for d in ds:
            company = cobjs_by_id[d['c_unique_id']]
            d.pop('c_unique_id')
            d.update(company=company, name=company.name + d['name'])
            if d['assess_date'] == '-':
                d.pop('assess_date')
            try:
                Department.objects.create(**d)
            except IntegrityError:
                pass

        # 更新营业部数量
        for cid in cobjs_by_id:
            company = cobjs_by_id[cid]
            company.department_count = Department.objects.filter(company=company).count()
            company.save()

        # 更新城市对应关系
        miss_citys = []
        for d in Department.objects.all():
            city_name = get_city_name_by_zip_code(d.zip_code)
            try:
                city = City.objects.get(city=city_name, location_type=2)
                d.city_id = city.id
                d.save()
            except City.DoesNotExist:
                miss_citys.append(city_name)
                continue

        miss_citys = list(set(miss_citys))
        for city_name in miss_citys:
            print (u'%s 未找到对应城市' % city_name).encode('utf8')

        # 更新证券公司图片信息
        for company in Company.objects.all():
            name = company.name
            file_name = (u'./kaihu/logo/%s.jpg' % name).encode('utf8')
            if not os.path.exists(file_name):
                raise Exception, (u'未扎到对应图片：%s' % name).encode('utf8')

            # temp = open(file_name, 'rb')
            # flag, img_name = qiniu_client.upload_img(temp, img_type="kaihu_company", file_name=company.id)
            flag, img_name = True, 'kaihu_company_%s' % company.id
            if flag:
                img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)
                company.img = img_name
                company.save()
            else:
                raise Exception, (u'图片上传失败：%s' % name).encode('utf8')

    # pprint(departments[0])
    # print len(departments)
    # print len(set([d['BUSINESS_CITY'] for d in departments]))
    print 'ok'


if __name__ == '__main__':
    init_city_zip_code()
    init_kaihu_info()
