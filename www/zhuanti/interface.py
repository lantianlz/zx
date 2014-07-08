# -*- coding: utf-8 -*-

from django.conf import settings

from common import cache, debug
from www.misc import consts
from www.zhuanti.models import Zhuanti


dict_err = {
    70100: u'专题已存在',
    70101: u'没有找到对应的专题',
    70102: u'专题名称已存在',
    70103: u'专题域名已存在',
}
dict_err.update(consts.G_DICT_ERROR)


class ZhuantiBase(object):

    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_zhuanti_by_id_or_domain(self, id_or_domain):
        try:
            return Zhuanti.objects.get(domain=id_or_domain)
        except Zhuanti.DoesNotExist:
            try:
                return Zhuanti.objects.get(id=id_or_domain)
            except:
                pass

    def get_all_zhuantis(self, state=True):
        objs = Zhuanti.objects.all()

        if state:
            objs = objs.filter(state=state)

        return objs

    def create_zhuanti(self, title, summary, img, domain, author_name, sort_num):
        try:
            assert title and summary and img and domain
        except:
            return 99800, dict_err.get(99800)
        if Zhuanti.objects.filter(title=title) or Zhuanti.objects.filter(domain=domain):
            return 70100, dict_err.get(70100)

        zhuanti = Zhuanti.objects.create(title=title, summary=summary, img=img, domain=domain, author_name=author_name, sort_num=sort_num)
        return 0, zhuanti

    def modify_zhuanti(self, zhuanti_id, **kwargs):
        if not zhuanti_id or not kwargs.get('title') or not kwargs.get('domain'):
            return 99800, dict_err.get(99800)

        zhuanti = self.get_zhuanti_by_id_or_domain(zhuanti_id)
        if not zhuanti:
            return 70101, dict_err.get(70101)

        temp = Zhuanti.objects.filter(title=kwargs.get('title'))
        if temp and temp[0].id != zhuanti.id:
            return 70102, dict_err.get(70102)

        temp = Zhuanti.objects.filter(domain=kwargs.get('domain'))
        if temp and temp[0].id != zhuanti.id:
            return 70103, dict_err.get(70103)

        try:
            for k, v in kwargs.items():
                setattr(zhuanti, k, v)

            zhuanti.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def remove_zhuanti(self, zhuanti_id):
        if not zhuanti_id:
            return 99800, dict_err.get(99800)

        zhuanti = self.get_zhuanti_by_id_or_domain(zhuanti_id)
        if not zhuanti:
            return 70101, dict_err.get(70101)

        try:
            zhuanti.state = False
            zhuanti.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)
