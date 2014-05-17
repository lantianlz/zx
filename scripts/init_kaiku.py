# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def init_kaihu_info():
    import json
    from pprint import pprint
    from django.db.utils import IntegrityError
    from www.kaihu.models import Company, Department

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

    pprint(departments[:1])
    print len(departments)
    # print len(set([d['BRANCH_UNIQUE_ID'] for d in departments]))
    print 'ok'


if __name__ == '__main__':
    init_kaihu_info()
