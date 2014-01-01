# -*- coding: utf-8 -*-


def format_external_user_info(info, source):
    d = {'nick': '', 'url': '', 'img': ''}
    if source == 'sina':
        d['nick'] = info['name']
        d['url'] = 'http://weibo.com/%s' % info['id']
        d['img'] = info['profile_image_url']
        d['gender'] = 0
    elif source == 'qq':
        d['nick'] = info['nickname']
        d['url'] = 'http://user.qzone.qq.com/'
        d['img'] = info['figureurl_2']
        d['gender'] = {u'男': 1, u'女': 2}.get(info['gender'], 1)
    return d
