# -*- coding: utf-8 -*-

import requests


def send_sms_by_weimi(mobiles, content):
    url = "http://api.weimi.cc/2/sms/send.html"
    uid = "R5KcEDTabEtb"
    pas = "5ka42gfe"

    if not mobiles:
        return

    if not isinstance(mobiles, (list, tuple)):
        mobiles = [mobiles, ]
    content = content.encode("utf8")
    try:
        for mobile in mobiles:
            mobile = mobile.encode("utf8")
            data = dict(uid=uid, pas=pas, mob=mobile, con=content, type="json")
            print url, data
            rep = requests.post(url, data=data, timeout=20)
            print rep.text.encode("utf8")
    except Exception, e:
        print e
        pass
    return 0


def send_sms_by_luosimao(mobiles, content):
    url = "http://api.weimi.cc/2/sms/send.html"
    uid = "R5KcEDTabEtb"
    pas = "5ka42gfe"

    if not mobiles:
        return

    if not isinstance(mobiles, (list, tuple)):
        mobiles = [mobiles, ]
    content = content.encode("utf8")
    try:
        for mobile in mobiles:
            mobile = mobile.encode("utf8")
            data = dict(uid=uid, pas=pas, mob=mobile, con=content, type="json")
            print url, data
            rep = requests.post(url, data=data, timeout=20)
            print rep.text.encode("utf8")
    except Exception, e:
        print e
        pass
    return 0


if __name__ == '__main__':
    content = u"【智选网】验证码：1348，有效期为十分钟。"
    send_sms_by_weimi(mobiles=u"13005012270", content=content)
