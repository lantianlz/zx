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
    content = (u'欢迎关注智选，这里有最新鲜的投资资讯、最睿智的投资问答。\n'
               u'点击底部菜单立即开启智选之旅，智选定不负你的关注')

    print wb.send_msg_to_weixin(content, to_user, app_key)
    # print wb.get_weixin_access_token(app_key="zhixuan_test")


if __name__ == '__main__':
    main()
