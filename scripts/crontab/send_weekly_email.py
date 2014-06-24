# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../www')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


import datetime
from common import utils
from www.question.interface import AnswerBase
from www.question.models import ImportantQuestion
from www.account.models import User
from www.tasks import async_send_email


def get_all_important_question():
    questions = []
    now = datetime.datetime.now().date()
    weekday = int(now.strftime('%w'))
    offset = (6 + weekday) if weekday > 0 else 13
    start_date = now - datetime.timedelta(days=offset)
    end_date = start_date + datetime.timedelta(days=7)
    important_questions = ImportantQuestion.objects.select_related('question').filter(question__state=True,
                                                                                      create_time__gt=start_date, create_time__lt=end_date)
    ab = AnswerBase()
    for iq in important_questions:
        for attr in ['img', 'img_alt', 'sort_num', 'operate_user_id']:
            question = iq.question
            setattr(question, attr, getattr(iq, attr))
        answer = ab.format_answers([ab.get_answers_by_question_id(question.id)[0], ])[0]

        question.answer = answer
        question.author = iq.get_author()
        question.iq_title = iq.title or question.title
        question.answer_summary = answer.get_summary(200)

        questions.append(question)
    return questions


def send_weekly_email():
    questions = get_all_important_question()
    if questions:
        context = dict(questions=questions)
        for user in User.objects.filter(state__gt=0):
            email = user.email
            context.update(dict(email=email))

        email = ["lz@zhixuan.com", "lcm@zhixuan.com", "jz@zhixuan.com"]
        async_send_email(email, u'智选每周精选', utils.render_email_template('email/important.html', context), 'html')

    print 'ok'


if __name__ == '__main__':
    send_weekly_email()
