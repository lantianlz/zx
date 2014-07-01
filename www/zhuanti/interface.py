# -*- coding: utf-8 -*-

from django.conf import settings

from common import cache, debug
from www.misc import consts
from www.zhuanti.models import Zhuanti


dict_err = {
    70100: u'专题已存在',
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

    def get_all_zhuantis(self):
        return Zhuanti.objects.filter(state=True)

    def create_zhuanti(self, title, summary, img, domain, author_name):
        try:
            assert title and summary and img and domain
        except:
            return 99800, dict_err.get(99800)
        if Zhuanti.objects.filter(title=title) or Zhuanti.objects.filter(domain=domain):
            return 70100, dict_err.get(70100)

        zhuanti = Zhuanti.objects.create(title=title, summary=summary, img=img, domain=domain, author_name=author_name)
        return 0, zhuanti
