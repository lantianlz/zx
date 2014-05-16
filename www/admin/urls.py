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

                        url(r'^important_question$', 'important_question'),
                        )


# 提问
urlpatterns += patterns('www.admin.views_question',
                        url(r'^question/search$', 'search'),
                        url(r'^question$', 'question'),
                        )
