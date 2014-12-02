# -*- coding: utf-8 -*-


"""
@note: sql直接操作方法封装
@author: lizheng
@date: 2014-12-01
"""


from django.db import connection, connections


def exec_sql(sql, database="default"):
    cursor = connections[database].cursor()
    cursor.execute(sql)
    return cursor.fetchall()
