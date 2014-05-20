# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
                       url(r'^$', 'home'),
                       )

# 推荐用户
urlpatterns += patterns('www.admin.views_recommend_user',

                        url(r'^recommend_user/get_user_by_nick$', 'get_user_by_nick'),
                        url(r'^recommend_user/set_recommend_user$', 'set_recommend_user'),
                        url(r'^recommend_user/un_recommend_user$', 'un_recommend_user'),
                        url(r'^recommend_user/set_recommend_user_sort$', 'set_recommend_user_sort'),
                        url(r'^recommend_user/get_all_recommend_users$', 'get_all_recommend_users'),
                        url(r'^recommend_user$', 'recommend_user'),
                        )

# 话题
urlpatterns += patterns('www.admin.views_topic',

                        url(r'^topic$', 'topic'),
                        )


# 每日精选
urlpatterns += patterns('www.admin.views_important_question',

                        url(r'^important_question/get_important_question_by_question_id$', 'get_important_question_by_question_id'),
                        url(r'^important_question/get_important_question_by_title$', 'get_important_question_by_title'),
                        url(r'^important_question/add_important$', 'add_important'),
                        url(r'^important_question/modify_important$', 'modify_important'),
                        url(r'^important_question/cancel_important$', 'cancel_important'),
                        url(r'^important_question$', 'important_question'),
                        )


# 提问
urlpatterns += patterns('www.admin.views_question',

                        url(r'^question/get_question_by_id$', 'get_question_by_id'),
                        url(r'^question/search$', 'search'),
                        url(r'^question$', 'question'),
                        )


# 权限
urlpatterns += patterns('www.admin.views_permission',

                        url(r'^permission/cancel_admin$', 'cancel_admin'),
                        url(r'^permission/save_user_permission$', 'save_user_permission'),
                        url(r'^permission/get_user_permissions$', 'get_user_permissions'),
                        url(r'^permission/get_all_administrators$', 'get_all_administrators'),
                        url(r'^permission$', 'permission'),
                        )


# 用户
urlpatterns += patterns('www.admin.views_user',

                        url(r'^user/get_user_by_id$', 'get_user_by_id'),
                        url(r'^user/search$', 'search'),
                        url(r'^user$', 'user'),
                        )
