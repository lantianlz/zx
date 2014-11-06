# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.kaihu.views',
                       url(r'^$', 'home'),
                       url(r'^d/(?P<district_id>\d+)$', 'department_list_by_district'),
                       url(r'^department_detail/(?P<department_id>\d+)$', 'department_detail'),
                       url(r'^get_customer_manager$', 'get_customer_manager'),
                       url(r'^get_departments_by_name$', 'get_departments_by_name'),
                       url(r'^article$', 'article_list'),
                       url(r'^article/(?P<article_id>\d+)$', 'article_detail'),
                       url(r'^news$', 'news_list'),
                       url(r'^news/(?P<news_id>\d+)$', 'news_detail'),
                       )


urlpatterns += patterns('www.kaihu.views_api',
                        url(r'^api_get_department_list$', 'api_get_department_list'),
                        url(r'^api_get_custom_manager_list$', 'api_get_custom_manager_list'),
                        url(r'^api_get_custom_manager_list_of_department$', 'api_get_custom_manager_list_of_department'),
                        url(r'^api_get_province_and_city$', 'api_get_province_and_city'),
                        url(r'^api_get_city_by_ip$', 'api_get_city_by_ip'),
                        )

urlpatterns += patterns('www.kaihu.views',
                        url(r'^(?P<city_abbr>\w+)$', 'department_list'),  # 此处必须放到最后，避免被误匹配
                        )
