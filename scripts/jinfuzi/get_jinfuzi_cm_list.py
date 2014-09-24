# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import datetime
import re
import time
import requests
from pyquery import PyQuery as pq
from www.kaihu.models import Jfzcm


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"}
domain = "http://www.jinfuzi.com"


def get_jinfuzi_cm_list():
    resp = requests.get("http://www.jinfuzi.com/department/", headers=headers, timeout=30)
    resp.encoding = "utf8"
    city_list = pq(resp.text)
    citys = city_list(".md_uc_box dd>a")

    print datetime.datetime.now()
    # 获取城市
    for city in citys:
        city = pq(city)
        city_url_first = city.attr("href")
        city_name = city.html()

        if city_name in [u"北京", u"上海", u"天津", u"重庆", u"茂名", u"云浮", u"清远", u"揭阳", u"中山", u"潮州", u"湛江", u"深圳", u"汕尾", u"惠州", u"梅州", u"珠海", u"东莞", u"肇庆", u"江门", u"佛山", u"汕头",
                         u"韶关", u"河源", u"广州", u"南通", u"启东", u"宿迁", u"南京", u"无锡", u"苏州", u"连云港", u"徐州", u"镇江", u"淮安", u"盐城", u"泰州", u"扬州", u"常州", u"济南", u"莱芜", u"青岛", u"潍坊", u"淄博",
                         u"东营", u"日照", u"泰安", u"菏泽", u"临沂", u"济宁", u"聊城", u"枣庄", u"德州", u"杭州", u"瑞安", u"温州", u"舟山", u"台州", u"嘉兴", u"衢州", u"绍兴", u"宁波", u"金华", u"郑州", u"周口", u"新乡",
                         u"洛阳", u"灵宝", u"孟州", u"漯河", u"驻马店", u"三门峡", u"开封", u"安阳", u"鹤壁", u"平顶山", u"商丘", u"濮阳", u"南阳", u"许昌", u"信阳", u"石家庄", u"承德", u"秦皇岛", u"保定", u"衡水", u"沧州",
                         u"邢台", u"邯郸", u"廊坊", u"唐山", u"沈阳", u"辽阳", u"营口", u"抚顺", u"大连", u"盘锦", u"成都", u"达州", u"宜宾", u"简阳市", u"南充", u"泸州", u"内江", u"巴中", u"广元"]:
            continue

        # 获取营业部
        for i in range(1, 50):
            print (u"第%s页处理中" % i).encode("utf8")
            city_url_split = city_url_first.split(".html", 1)
            city_url = "%s-p%s.html" % (city_url_split[0], i)

            resp = requests.get(city_url, headers=headers, timeout=30)
            resp.encoding = "utf8"
            department_list = pq(resp.text)
            departments = department_list(".list-content li dt a")

            break_flag = False
            break_flag_count = 0
            for department in departments:
                department = pq(department)
                department_url = department.attr("href")
                department_name = department.html()

                # 获取客户经理
                resp = requests.get(department_url, headers=headers, timeout=30)
                resp.encoding = "utf8"
                cm_list = pq(resp.text)
                cms_vip = cm_list(".yyby-content-list-vip h3 a:odd")
                cms_normal = cm_list(".yyby-content-list h3 a:odd")

                cms = []
                for cm in cms_vip:
                    cm = pq(cm)
                    cms.append([u"付费用户", cm.html(), cm.attr("href")])

                for cm in cms_normal:
                    cm = pq(cm)
                    cms.append([u"未付费用户", cm.html(), cm.attr("href")])

                for cm in cms:
                    pay_type = cm[0]
                    name = cm[1]
                    href = cm[2] if cm[2].startswith("http") else ("%s%s" % (domain, cm[2]))

                    try:
                        for i in range(3):
                            resp = requests.get(href, headers=headers, timeout=10)
                            resp.encoding = "utf8"
                            cm_single = pq(resp.text)
                            break
                    except:
                        continue

                    mobile_pq = cm_single(".phone-num")
                    qq_pq = cm_single(".zixun-qq")
                    mobile = mobile_pq.html() if mobile_pq else u""
                    qq = u""
                    if qq_pq:
                        _qq = qq_pq.attr("href")
                        if "qq=" in _qq:
                            qq = _qq.split("qq=")[1].split("&")[0]

                    print pay_type.encode("utf8"), name.encode("utf8"), href, mobile.encode("utf8"), qq.encode("utf8")
                    try:
                        Jfzcm.objects.create(name=name, href=href, pay_type=pay_type, city_name=city_name, department_name=department_name, mobile=mobile, qq=qq)
                    except:
                        print u"creat error"

                    # print city_name.encode("utf8"), department_name.encode("utf8")

                if not cms:
                    break_flag_count += 1
                    if break_flag_count > 3:
                        break_flag = True
                        break
                else:
                    break_flag_count = 0

            if break_flag or len(departments) < 10:
                break
            # break

        print datetime.datetime.now(), (u"%s, ok" % city_name).encode("utf8")
        # break
    print u"ok"

if __name__ == '__main__':
    get_jinfuzi_cm_list()
