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
    continue_flag = True
    # 获取城市
    for city in citys:
        city = pq(city)
        city_url_first = city.attr("href")
        city_name = city.html()

        # if city_name != u"岳阳" and continue_flag:
        #     continue
        # else:
        #     continue_flag = False

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
                for i in range(3):
                    try:
                        resp1 = requests.get(department_url, headers=headers, timeout=10)
                        break
                    except:
                        print u"timeout in line 66"

                resp1.encoding = "utf8"
                cm_list = pq(resp1.text)
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
