# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
                       url(r'^$', 'home'),
                       )


urlpatterns += patterns('www.admin.views_recommend_user',

                        url(r'^recommend_user/get_user_by_nick$', 'get_user_by_nick'),
                        url(r'^recommend_user/set_recommend_user$', 'set_recommend_user'),
                        url(r'^recommend_user/un_recommend_user$', 'un_recommend_user'),
                        url(r'^recommend_user/set_recommend_user_sort$', 'set_recommend_user_sort'),
                        url(r'^recommend_user/get_all_recommend_users$', 'get_all_recommend_users'),
                        url(r'^recommend_user$', 'recommend_user'),
                        )
