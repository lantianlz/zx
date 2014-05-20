# -*- coding: utf-8 -*-

import json
from django.core.management.base import BaseCommand

from misc import consts

from admin.models import Permission


class Command(BaseCommand):

    def handle(self, *args, **options):
        print u'==================初始化权限数据开始...'
        print

        cache = {}

        for p in consts.PERMISSIONS:

            obj, created = Permission.objects.get_or_create(name=p['name'], code=p['code'])

            cache[obj.code] = obj.id

            # 设置父节点
            if p['parent']:
                obj.parent_id = cache[p['parent']]
                obj.save()

        print
        print u'==================完成'
