# -*- coding: utf-8 -*-

import time
import logging
from django.http import Http404
from django.conf import settings
from common import debug


class UserMiddware(object):

    def __init__(self):
        pass

    def process_request(self, request):
        setattr(request, "_process_start_timestamp", time.time())

    def process_response(self, request, response):
        if hasattr(request, '_process_start_timestamp'):
            t = int((time.time() - float(getattr(request, '_process_start_timestamp'))))
            if t >= 10:
                user_id = request.user.id if request.user.is_authenticated() else "anymouse"
                logging.error("LONG_PROCESS: %s %s %s" % (request.path, t, user_id))
        return response

    def process_exception(self, request, exception):
        # print '*' * 50 + 'debug info start' + '*' * 50
        if type(exception) == Http404:
            return

        url = request.path
        # ext_data = {"url": url, "method": request.method,
        #             "query_string": ",".join(["".join([k, request.REQUEST.get(k)]) for k in request.REQUEST])}
        title = u'%s error in %s' % (settings.SERVER_NAME, url)
        content = debug.get_debug_detail(exception)
        # print '*' * 50 + 'debug info end' + '*' * 50
        if settings.SERVER_NAME != 'DEVELOPER':  # not settings.DEBUG or True:
            from www.tasks import async_send_email
            async_send_email(settings.NOTIFICATION_EMAIL, title, content)
