# -*- coding: utf-8 -*-

'''
全局常量维护
'''

G_DICT_ERROR = {
    99600: u'不存在的用户',
    99700: u'权限不足',
    99800: u'参数缺失',
    99900: u'系统错误',
    0: u'成功'
}


PERMISSIONS = [
    #{'code': 'is_administrator', 'name': u'能否进入管理后台', 'parent': None},
    {'code': 'permission_manage', 'name': u'权限管理', 'parent': None},
    {'code': 'add_user_permission', 'name': u'添加用户权限', 'parent': 'permission_manage'},
    {'code': 'query_user_permission', 'name': u'查询用户权限', 'parent': 'permission_manage'},
    {'code': 'modify_user_permission', 'name': u'修改用户权限', 'parent': 'permission_manage'},
    {'code': 'cancel_admin', 'name': u'取消管理员', 'parent': 'permission_manage'},

    {'code': 'manage_recommend_user', 'name': u'推荐用户管理', 'parent': None},
    {'code': 'set_recommend_user', 'name': u'设置推荐用户', 'parent': 'manage_recommend_user'},
    {'code': 'query_recommend_user', 'name': u'查询推荐用户信息', 'parent': 'manage_recommend_user'},
    {'code': 'modify_recommend_user', 'name': u'修改推荐用户顺序', 'parent': 'manage_recommend_user'},
    {'code': 'cancel_recommend_user', 'name': u'取消推荐用户', 'parent': 'manage_recommend_user'},

    {'code': 'important_question_manage', 'name': u'每日精选管理', 'parent': None},
    {'code': 'add_important_question', 'name': u'添加每日精选', 'parent': 'important_question_manage'},
    {'code': 'query_important_question', 'name': u'查询每日精选', 'parent': 'important_question_manage'},
    {'code': 'modify_important_question', 'name': u'修改每日精选', 'parent': 'important_question_manage'},
    {'code': 'cancel_important_question', 'name': u'取消每日精选', 'parent': 'important_question_manage'},

    {'code': 'question_manage', 'name': u'提问管理', 'parent': None},
    #{'code': 'add_question', 'name': u'添加提问', 'parent': 'question_manage'},
    {'code': 'query_question', 'name': u'查询提问', 'parent': 'question_manage'},
    {'code': 'modify_question', 'name': u'修改提问', 'parent': 'question_manage'},
    {'code': 'remove_question', 'name': u'删除提问', 'parent': 'question_manage'},

    {'code': 'user_manage', 'name': u'用户管理', 'parent': None},
    #{'code': 'add_user', 'name': u'添加用户', 'parent': 'user_manage'},
    {'code': 'query_user', 'name': u'查询用户', 'parent': 'user_manage'},
    {'code': 'modify_user', 'name': u'修改用户', 'parent': 'user_manage'},
    {'code': 'remove_user', 'name': u'删除用户', 'parent': 'user_manage'},

    {'code': 'customer_manager_manage', 'name': u'客户经理管理', 'parent': None},
    {'code': 'add_customer_manager', 'name': u'添加客户经理', 'parent': 'customer_manager_manage'},
    {'code': 'query_customer_manager', 'name': u'查询客户经理', 'parent': 'customer_manager_manage'},
    {'code': 'modify_customer_manager', 'name': u'修改客户经理', 'parent': 'customer_manager_manage'},
    {'code': 'remove_customer_manager', 'name': u'删除客户经理', 'parent': 'customer_manager_manage'},

    {'code': 'friendly_link_manage', 'name': u'友情链接管理', 'parent': None},
    {'code': 'add_friendly_link', 'name': u'添加友情链接', 'parent': 'friendly_link_manage'},
    {'code': 'query_friendly_link', 'name': u'查询友情链接', 'parent': 'friendly_link_manage'},
    {'code': 'modify_friendly_link', 'name': u'修改友情链接', 'parent': 'friendly_link_manage'},
    {'code': 'remove_friendly_link', 'name': u'删除友情链接', 'parent': 'friendly_link_manage'},

    {'code': 'statistics_manage', 'name': u'统计管理', 'parent': None},
    {'code': 'statistics_active_user', 'name': u'当日活跃用户统计', 'parent': 'statistics_manage'},
    {'code': 'statistics_register_user', 'name': u'注册用户统计', 'parent': 'statistics_manage'},

    {'code': 'tools', 'name': u'常用工具', 'parent': None},
    {'code': 'get_cache', 'name': u'查询缓存', 'parent': 'tools'},
    {'code': 'remove_cache', 'name': u'删除缓存', 'parent': 'tools'},
    {'code': 'modify_cache', 'name': u'修改缓存', 'parent': 'tools'},
    {'code': 'query_notice', 'name': u'查询全站通告', 'parent': 'tools'},
    {'code': 'add_notice', 'name': u'添加全站通告', 'parent': 'tools'},
    {'code': 'modify_notice', 'name': u'修改全站通告', 'parent': 'tools'},
    {'code': 'remove_notice', 'name': u'删除全站通告', 'parent': 'tools'},

    {'code': 'topic_manage', 'name': u'话题管理', 'parent': None},
    {'code': 'add_topic', 'name': u'添加话题', 'parent': 'topic_manage'},
    {'code': 'query_topic', 'name': u'查询话题', 'parent': 'topic_manage'},
    {'code': 'modify_topic', 'name': u'修改话题', 'parent': 'topic_manage'},
    #{'code': 'remove_topic', 'name': u'查询全站通告', 'parent': 'topic_manage'},
]
