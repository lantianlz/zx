# -*- coding: utf-8 -*-

from celery.task import task


@task(queue='email_worker', name='email_worker.email_send')
def async_send_email(emails, title, content, type='text'):
    from common import utils
    content = '''%s
	该邮件由智选网自动发送，请勿直接回复
	''' % content
    return utils.send_email(emails, title, content, type='text')
