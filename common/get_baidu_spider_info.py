# -*- coding: utf-8 -*-
"""
@note: 分析ngxin日志，提取出百度蜘蛛信息
"""

import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


import commands
import datetime
from pprint import pprint


def get_baidu_spider_info():
    cmd_baidu = """grep -i Baiduspider /var/log/nginx/www.log"""
    datas = commands.getoutput(cmd_baidu)
    lst_info = []
    lst_invalid_info = []
    dict_info_group_by_url = {}

    for data in datas.split("\n"):
        data = data.strip().split()
        if data:
            # print data
            state = data[8]
            access_time = datetime.datetime.strptime(data[3].split()[0][1:], '%d/%b/%Y:%H:%M:%S')
            lst_info.append([data[0], access_time.strftime("%Y-%m-%d %H:%M:%S"), data[6], state])
            if state != "200":
                lst_invalid_info.append([data[0], access_time.strftime("%Y-%m-%d %H:%M:%S"), data[6], state])

    for info in lst_info:
        count = dict_info_group_by_url.get(info[2], 0)
        dict_info_group_by_url[info[2]] = count + 1

    lst_info_group_by_url = dict_info_group_by_url.items()
    lst_info_group_by_url.sort(key=lambda x: x[1], reverse=True)

    pprint(lst_info)
    # pprint(lst_info_group_by_url)
    # pprint(lst_invalid_info)


if __name__ == '__main__':
    get_baidu_spider_info()
