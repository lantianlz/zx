# -*- coding: utf-8 -*-

from celery.task import task


@task(queue='email_worker', name='email_worker.email_send')
def async_send_email(emails, title, content, type='text'):
    from common import utils
    return utils.send_email(emails, title, content, type)


@task(queue='www_worker', name='www_worker.async_clear_count_info_by_code')
def async_clear_count_info_by_code(user_id, code):
    from www.message import interface
    return interface.UnreadCountBase().clear_count_info_by_code(user_id, code)


@task(queue='one_by_one_worker', name='one_by_one_worker.add_question_view_count')
def async_add_question_view_count(question_id):
    '''
    @note: 异步更新浏览次数
    '''
    from www.question.interface import QuestionBase
    QuestionBase().add_question_view_count(question_id)
