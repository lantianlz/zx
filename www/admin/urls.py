# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
                       url(r'^$', 'home'),
                       )


# 话题
urlpatterns += patterns('www.admin.views_topic',

                        url(r'^topic/add_topic$', 'add_topic'),
                        url(r'^topic/get_topic_by_id$', 'get_topic_by_id'),
                        url(r'^topic/modify_topic$', 'modify_topic'),
                        url(r'^topic/search$', 'search'),
                        url(r'^topic/get_topics_by_name$', 'get_topics_by_name'),
                        url(r'^topic$', 'topic'),
                        )


# 提问
urlpatterns += patterns('www.admin.views_question',

                        url(r'^question/question/get_question_by_id$', 'get_question_by_id'),
                        url(r'^question/question/search$', 'search'),
                        url(r'^question/question$', 'question'),
                        )
# 每日精选
urlpatterns += patterns('www.admin.views_important_question',

                        url(r'^question/important_question/get_important_question_by_question_id$', 'get_important_question_by_question_id'),
                        url(r'^question/important_question/get_important_question_by_title$', 'get_important_question_by_title'),
                        url(r'^question/important_question/add_important$', 'add_important'),
                        url(r'^question/important_question/modify_important$', 'modify_important'),
                        url(r'^question/important_question/cancel_important$', 'cancel_important'),
                        url(r'^question/important_question$', 'important_question'),
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

                        url(r'^user/user/modify_user$', 'modify_user'),
                        url(r'^user/user/get_user_by_id$', 'get_user_by_id'),
                        url(r'^user/user/search$', 'search'),
                        url(r'^user/user$', 'user'),
                        )
# 推荐用户
urlpatterns += patterns('www.admin.views_recommend_user',

                        url(r'^user/recommend_user/get_user_by_nick$', 'get_user_by_nick'),
                        url(r'^user/recommend_user/set_recommend_user$', 'set_recommend_user'),
                        url(r'^user/recommend_user/un_recommend_user$', 'un_recommend_user'),
                        url(r'^user/recommend_user/set_recommend_user_sort$', 'set_recommend_user_sort'),
                        url(r'^user/recommend_user/get_all_recommend_users$', 'get_all_recommend_users'),
                        url(r'^user/recommend_user$', 'recommend_user'),
                        )
# 客户经理
urlpatterns += patterns('www.admin.views_customer_manager',

                        url(r'^user/customer_manager/get_customer_manager_by_user_id$', 'get_customer_manager_by_user_id'),
                        url(r'^user/customer_manager/delete_customer_manager$', 'delete_customer_manager'),
                        url(r'^user/customer_manager/modify_customer_manager$', 'modify_customer_manager'),
                        url(r'^user/customer_manager/add_customer_manager$', 'add_customer_manager'),
                        url(r'^user/customer_manager/search$', 'search'),
                        url(r'^user/customer_manager/get_departments_by_name$', 'get_departments_by_name'),
                        url(r'^user/customer_manager/get_citys_by_name$', 'get_citys_by_name'),
                        url(r'^user/customer_manager$', 'customer_manager'),
                        )


# 友情链接
urlpatterns += patterns('www.admin.views_friendly_link',

                        url(r'^friendly_link/modify_friendly_link$', 'modify_friendly_link'),
                        url(r'^friendly_link/remove_friendly_link$', 'remove_friendly_link'),
                        url(r'^friendly_link/get_friendly_link_by_id$', 'get_friendly_link_by_id'),
                        url(r'^friendly_link/add_friendly_link$', 'add_friendly_link'),
                        url(r'^friendly_link/search$', 'search'),
                        url(r'^friendly_link$', 'friendly_link'),
                        )


# 营业部
urlpatterns += patterns('www.admin.views_department',

                        url(r'^department/get_company_by_name$', 'get_company_by_name'),
                        url(r'^department/get_department_by_id$', 'get_department_by_id'),
                        url(r'^department/search$', 'search'),
                        url(r'^department$', 'department'),
                        )


# 统计
urlpatterns += patterns('www.admin.views_statistics',

                        url(r'^statistics/statistic_register_user$', 'statistic_register_user'),
                        url(r'^statistics/get_active_user$', 'get_active_user'),
                        url(r'^statistics/active_user$', 'active_user'),
                        url(r'^statistics/register_user$', 'register_user'),
                        )


# 常用工具
urlpatterns += patterns('www.admin.views_tools',
                        # 通知管理
                        url(r'^tools/notice/remove_notice$', 'remove_notice'),
                        url(r'^tools/notice/modify_notice$', 'modify_notice'),
                        url(r'^tools/notice/get_notice_by_id$', 'get_notice_by_id'),
                        url(r'^tools/notice/add_notice$', 'add_notice'),
                        url(r'^tools/notice/search_notice$', 'search_notice'),
                        url(r'^tools/notice$', 'notice'),

                        # 缓存管理
                        url(r'^tools/caches/get_cache$', 'get_cache'),
                        url(r'^tools/caches/remove_cache$', 'remove_cache'),
                        url(r'^tools/caches/modify_cache$', 'modify_cache'),
                        url(r'^tools/caches$', 'caches'),
                        )
