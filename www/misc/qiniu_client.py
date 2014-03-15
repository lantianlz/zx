# -*- coding: utf-8 -*-


"""
@attention: 七牛客户端
@author: lizheng
@date: 2014-03-15
"""

import qiniu.rs
from django.conf import settings

HASH_KEY = 'zhixuanimg20140315'
AK = 'DdZbYWvnh7XAEnu9s4WqnbN-7_0qM23lcKitiKrx'
SK = '1VU-ve9ecmMDFBRvI-pWxTsW4oq4uS-c1Ea5WuxP'

qiniu.conf.ACCESS_KEY = AK
qiniu.conf.SECRET_KEY = SK


def get_upload_token(img_key=None, img_type='avatar', scope='zimg0'):
    if img_key:
        scope = '%s:%s' % (scope, img_key)
    if img_type == 'avatar':
        returnUrl = '%s/qiniu_img_return' % settings.MAIN_DOMAIN
    returnBody = ('{"user_id":$(x:user_id), "img_type":$(x:img_type), "key":$(key),  "hash":$(etag), "w":$(imageInfo.width), '
                  '"h":$(imageInfo.height), "bucket":$(bucket)}')

    policy = qiniu.rs.PutPolicy(scope=scope)
    policy.returnUrl = returnUrl
    policy.returnBody = returnBody
    policy.insertOnly = 1
    uptoken = policy.token()
    return uptoken


if __name__ == '__main__':
    get_upload_token()
