# -*- coding: utf-8 -*-


"""
@attention: utils方法封装
@author: lizheng
@date: 2013-12-09
"""


def uuid_without_dash():
	import uuid
	return str(uuid.uuid1()).replace('-', '')


def get_clientip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        client_ip = request.META['HTTP_X_FORWARDED_FOR']
        arr_ip = client_ip.split(',', 1)
        return arr_ip[0].strip()
    elif 'HTTP_X_REAL_IP' in request.META:
        return request.META['HTTP_X_REAL_IP']
    else:
        return request.META.get('REMOTE_ADDR', u'127.0.0.1')


def time_format(value):
    import time
    import datetime

    if not value:
        return 'datetime error'
    d = value
    if not isinstance(value, datetime.datetime):
        d = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    now_date = datetime.datetime.now()
    ds = time.time() - time.mktime(d.timetuple())  # 秒数
    # dd = now_date - d  # 日期相减对象
    if ds <= 5:
        return u'刚刚'
    if ds < 60:
        return u'%d秒前' % ds
    if ds < 3600:
        return u'%d分钟前' % (ds / 60,)
    d_change = now_date.day - d.day
    if ds < 3600 * 24 * 3:
        if d_change == 0:
            return u'今天%s' % d.strftime('%H:%M:%S')
        if d_change == 1:
            return u'昨天%s' % d.strftime('%H:%M:%S')
        if d_change == 2:
            return u'前天%s' % d.strftime('%H:%M:%S')
    y_change = now_date.year - d.year
    if y_change == 0:
        return u'%s' % d.strftime('%m-%d %H:%M:%S')
    if y_change == 1:
        return u'去年%s' % d.strftime('%m-%d %H:%M:%S')
    return u'%s年前%s' % (y_change, unicode(d.strftime('%m月%d日'), 'utf8'))


def send_email(emails, title, content, type='text'):
    from django.conf import settings
    from django.core.mail import send_mail, EmailMessage

    if not emails:
        return

    if not isinstance(emails, (list, tuple)):
        emails = [emails, ]

    if type != 'html':
        send_mail(title, content, settings.EMAIL_FROM, emails, fail_silently=True)
    else:
        msg = EmailMessage(title, content, settings.EMAIL_FROM, emails)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    return 0


def get_next_url(request):
    from django.conf import settings
    from urlparse import urlparse
    next_url = request.REQUEST.get('next_url')
    if not next_url:
        referrer = request.META.get('HTTP_REFERER')
        if referrer and referrer.startswith(settings.MAIN_DOMAIN):
            referrer = list(urlparse(referrer))[2]
            if referrer != request.path and referrer not in ('/regist', '/'):
                # referrer的query参数会丢失
                next_url = referrer + '?' + list(urlparse(referrer))[4]
    return next_url or '/home'