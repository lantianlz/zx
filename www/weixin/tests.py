# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = 'f762a6f5d2b711e39a09685b35d0bf16'


def main():
    from www.weixin.interface import WexinBase
    wb = WexinBase()
    app_key = "zhixuan_test"
    to_user = 'o07dat0ujliP84s4GPsLFXOrAcbk'
    content = (u'古人云：鸟随鸾凤飞腾远，人伴贤良品质高。\n'
               u'古人又云：物以类聚，人以群分。\n'
               u'想要成为什么样的人，最好的办法是先交上这样的朋友。\n'
               u'你想成为一流的投资者吗？你想享受一流的咨询、互动服务吗？'
               u'智选投资问答社区有国内主流券商投资顾问、公（私）募基金研究员、投资大拿。\n\n'
               u'关注智选，你最智慧的选择')

    print wb.send_msg_to_weixin(content, to_user, app_key)
    # print wb.get_weixin_access_token(app_key="zhixuan_test")


if __name__ == '__main__':
    main()
