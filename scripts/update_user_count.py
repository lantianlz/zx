# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def update_user_count():
    from www.account.models import UserCount, User
    from www.question.interface import QuestionBase, AnswerBase, LikeBase
    from www.timeline.interface import UserFollowBase

    for user in User.objects.all():
        user_id = user.id
        user_question_count = QuestionBase().get_user_question_count(user_id)
        user_answer_count = AnswerBase().get_user_sended_answers_count(user_id)
        user_liked_count = LikeBase().get_user_liked_count(user_id)
        following_count = UserFollowBase().get_following_count(user_id)
        follower_count = UserFollowBase().get_follower_count(user_id)

        if user_question_count or user_answer_count or user_liked_count or following_count or follower_count:
            user_count, created = UserCount.objects.get_or_create(user_id=user_id)
            user_count.user_question_count = user_question_count
            user_count.user_answer_count = user_answer_count
            user_count.user_liked_count = user_liked_count
            user_count.following_count = following_count
            user_count.follower_count = follower_count
            user_count.save()

    print 'ok'


if __name__ == '__main__':
    update_user_count()
