# -*- coding: utf-8 -*-


"""
@attention: utils方法封装
@author: lizheng
@date: 2013-12-09
"""

import re


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
            if referrer != request.path and referrer not in ('/regist', '/', '/reset_password'):
                # referrer的query参数会丢失
                next_url = referrer + '?' + list(urlparse(referrer))[4]
    return next_url or '/home'


def filter_script(htmlstr):
    '''
    @note: html内容过滤 去掉script,link,外联style,标签上面的事件，标签上面样式含expression,javascript
    '''
    # 先过滤CDATA
    re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
    re_script = re.compile('<\s*script[^>]*>.*<\s*/\s*script\s*>', re.I)  # Script
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
    re_link = re.compile('<\s*link[^>]*>', re.I)  # 外联link
    re_comment = re.compile('<!--[^>]*-->')  # HTML注释

    # 过滤html元素节点里面的 expression,javascript,document,cookie,on
    # re_expression = re.compile('<[^>]*(expression|javascript|document|cookie|\s+on)+[^>]*>[^<]*<\s*/\s*[^>]*\s*>', re.I)

    # 去掉多余的空行
    blank_line = re.compile('\n+')
    s = blank_line.sub('\n', htmlstr)

    s = re_cdata.sub('', s)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_link.sub('', s)  # 外联link
    s = re_comment.sub('', s)  # 去掉HTML注释
    # s = re_expression.sub('', s)  # 去掉样式中expression表达式

    re_expression = re.compile('<[^>]*( on)[^>]*>', re.I)
    s = re_expression.sub('', s)  # 去掉html带on事件的

    # 去掉多余的空行
    s = blank_line.sub('\n', s)
    return s


def render_template(template_path='', context={}):
    '''
    @note: 渲染模板
    '''
    from django import template 

    if not template_path:
        return ''

    t = template.loader.get_template(template_path)
    c = template.Context(context)
    return t.render(c)
