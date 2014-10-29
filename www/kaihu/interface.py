# -*- coding: utf-8 -*-

import datetime
from django.db import transaction
from django.db.models import Q

from common import cache, debug, utils
from www.misc.decorators import cache_required
from www.misc import consts
from www.account.interface import UserBase, UserCountBase
from www.kaihu.models import Company, Department, City, CustomerManager, FriendlyLink, Article, News, Jfzcm


dict_err = {
    50100: u'找不到指定用户',
    50101: u'找不到指定营业部',
    50102: u'找不到指定客户经理',
    50103: u'找不到指定友情链接',
    50104: u'找不到指定资讯',
    50105: u'城市拼音重复',
    50106: u'城市拼音简写重复',
}
dict_err.update(consts.G_DICT_ERROR)

KAIHU_DB = 'kaihu'


class CityBase(object):

    def __init__(self):
        pass

    def get_all_areas(self):
        return City.objects.filter(location_type=0)

    def get_all_provinces(self):
        return City.objects.filter(location_type=1)

    def get_all_citys(self):
        return City.objects.filter(location_type=2)

    def get_all_districts(self):
        return City.objects.filter(location_type=3)

    def get_all_city_group_by_province(self):
        data = []
        areas = self.get_all_areas()
        provinces = City.objects.filter(location_type=1)
        citys = self.get_all_citys()

        for area in areas:
            area_provices = provinces.filter(area=area.id)
            data_citys = []
            for ap in area_provices:
                province_citys = citys.filter(province=ap.id)
                data_citys.append([ap, province_citys])
            data.append([area, data_citys])
        return data
    
    def get_citys_by_province(self, province_id):
        return self.get_all_citys().filter(province=province_id)

    def get_city_by_pinyin_abbr(self, pinyin_abbr):
        if pinyin_abbr:
            citys = self.get_all_citys().filter(pinyin_abbr=pinyin_abbr)
            if citys:
                return citys[0]

    def get_city_by_pinyin(self, pinyin):
        if pinyin:
            citys = self.get_all_citys().filter(pinyin=pinyin)
            if citys:
                return citys[0]

    def get_city_by_id(self, city_id):
        if city_id:
            citys = self.get_all_citys().filter(id=city_id)
            if citys:
                return citys[0]

    def get_citys_by_name(self, city_name):
        citys = []

        if city_name:
            citys = self.get_all_citys().filter(city__contains=city_name)

        return citys

    def get_one_city_by_name(self, city_name):
        objs = self.get_all_citys().filter(city=city_name)
        if objs:
            return objs[0]
        return None

    @cache_required(cache_key='province_by_id_%s', expire=3600 * 24)
    def get_province_by_id(self, province_id):
        objs = self.get_all_provinces().filter(id=province_id)
        if objs:
            return objs[0]

    def search_citys_for_admin(self, city_name, is_show=0, sort_by_province=True):
        citys = self.get_all_citys().filter(is_show=is_show)

        if city_name:
            citys = citys.filter(city__contains=city_name)

        if sort_by_province:
            citys = citys.order_by('-province')

        return citys

    def modify_city(self, city_id, **kwargs):

        if not city_id:
            return 99800, dict_err.get(99800)

        city = self.get_city_by_id(city_id)

        if not city:
            return 99800, dict_err.get(99800)

        if kwargs.get('pinyin'):
            temp = self.get_city_by_pinyin(kwargs.get('pinyin'))
            if temp and temp.id != city.id:
                return 50105, dict_err.get(50105)

        if kwargs.get('pinyin_abbr'):
            temp = self.get_city_by_pinyin_abbr(kwargs.get('pinyin_abbr'))
            if temp and temp.id != city.id:
                return 50106, dict_err.get(50106)

        try:
            for k, v in kwargs.items():
                setattr(city, k, v)

            city.save()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    # @cache_required(cache_key='city_baidu_rank_%s', expire=3600 * 24)
    # def get_city_baidu_rank(self, city_id_or_object):
    #     from common.utils import get_baidu_rank

    #     city = city_id_or_object
    #     if not isinstance(city_id_or_object, City):
    #         city = self.get_city_by_id(city_id_or_object)
    #     if city.is_show:
    #         return get_baidu_rank(key=u"%s股票开户" % city.get_city_name_for_seo())
    #     else:
    #         return u"暂无"

    def get_district_by_id(self, district_id):
        if district_id:
            districts = self.get_all_districts().filter(id=district_id)
            if districts:
                return districts[0]

    def get_districts_by_city(self, city_id, is_show=1):
        districts = []
        if city_id:
            ps = dict(city=city_id)
            if is_show is not None:
                ps.update(dict(is_show=is_show))
            districts = self.get_all_districts().filter(**ps)

        return districts

    def search_districts_for_admin(self, district_name, city_name, is_show=0):
        districts = self.get_all_districts().filter(is_show=is_show)

        if city_name:
            city = self.get_one_city_by_name(city_name)
            if city:
                districts = districts.filter(city=city.id)

        if district_name:
            districts = districts.filter(district__contains=district_name)

        return districts

    def modify_district(self, district_id, **kwargs):

        if not district_id:
            return 99800, dict_err.get(99800)

        district = self.get_district_by_id(district_id)

        if not district:
            return 99800, dict_err.get(99800)

        # if kwargs.get('pinyin'):
        #     temp = self.get_city_by_pinyin(kwargs.get('pinyin'))
        #     if temp and temp.id != city.id:
        #         return 50105, dict_err.get(50105)

        # if kwargs.get('pinyin_abbr'):
        #     temp = self.get_city_by_pinyin_abbr(kwargs.get('pinyin_abbr'))
        #     if temp and temp.id != city.id:
        #         return 50106, dict_err.get(50106)

        try:
            for k, v in kwargs.items():
                setattr(district, k, v)

            district.save()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)


class DepartmentBase(object):

    def __init__(self):
        pass

    def get_all_departments(self):
        return Department.objects.select_related('company').all()

    def get_departments_by_city_id(self, city_id):
        return list(self.get_all_departments().filter(city_id=city_id).exclude(des=None))

    def get_departments_by_district_id(self, district_id):
        return list(self.get_all_departments().filter(district_id=district_id).exclude(des=None))

    def get_departments_by_random(self, city_id):
        return list(self.get_all_departments().filter(city_id=city_id).exclude(des=None).order_by('?'))

    def get_department_by_id(self, department_id):
        try:
            department = self.get_all_departments().filter(id=department_id)[0]
            department.city = CityBase().get_city_by_id(department.city_id)
            department.district = CityBase().get_district_by_id(department.district_id)
        except Exception:
            department = None
        return department

    def get_departments_by_name(self, department_name):
        departments = self.get_all_departments()
        if department_name:
            departments = departments.filter(name__contains=department_name)
        return departments

    def search_departments_for_admin(self, department_name, city_name, des_state):
        departments = self.get_departments_by_name(department_name)

        if city_name:
            city = CityBase().get_one_city_by_name(city_name)
            if city:
                departments = departments.filter(city_id=city.id)

        total = departments.count()

        # 描述不为空
        if des_state == '1':
            departments = departments.exclude(Q(des__isnull=True) | Q(des=''))

        # 描述为空
        if des_state == '2':
            departments = departments.filter(Q(des__isnull=True) | Q(des=''))

        return departments, total

    def modify_department(self, department_id, **kwargs):
        if not department_id:
            return 99800, dict_err.get(99800)

        department = self.get_department_by_id(department_id)
        if not department:
            return 50101, dict_err.get(50101)

        company_id = kwargs.get("company_id")
        if company_id and str(company_id) != str(department.company_id):
            old_company = department.company
            old_company.department_count -= 1
            old_company.save()

            new_company = CompanyBase().get_company_by_id(company_id)
            new_company.department_count += 1
            new_company.save()

        try:
            for k, v in kwargs.items():
                setattr(department, k, v)

            department.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def add_department(self, company_id, name, des, addr, tel, city_id, district_id, sort_num=0):
        if None in (company_id, name):
            return 99800, dict_err.get(99800)
        import time
        try:
            obj = Department.objects.create(
                company_id=company_id, name=name, des=des, addr=addr, tel=tel,
                city_id=city_id, district_id=district_id, sort_num=sort_num, unique_id=int(time.time())
            )

            company = CompanyBase().get_company_by_id(company_id)
            company.department_count += 1
            company.save()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, obj


class CustomerManagerBase(object):

    def __init__(self):
        pass

    def format_customer_managers(self, objs):
        for obj in objs:
            obj.user = UserBase().get_user_by_id(obj.user_id)
            obj.user.user_count_info = UserCountBase().get_user_count_info(obj.user_id)
            obj.department = DepartmentBase().get_department_by_id(obj.department.id)   # 得到city信息
        return objs

    def format_customer_managers_for_ajax(self, objs):
        data = []
        for obj in objs:
            if not obj:
                continue
            
            user = UserBase().get_user_by_id(obj.user_id)
            user_count_info = UserCountBase().get_user_count_info(obj.user_id)
            data.append(dict(user_id=user.id, user_nick=user.nick, user_avatar=user.get_avatar_100(),
                             department_name=obj.department.get_short_name(), company_short_name=obj.department.company.get_short_name(),
                             department_id=obj.department.id, city_id=obj.city_id,
                             sort_num=obj.sort_num, vip_info=obj.vip_info, qq=obj.qq, mobile=obj.mobile, pay_type=obj.pay_type,
                             user_question_count=user_count_info['user_question_count'], user_answer_count=user_count_info['user_answer_count'],
                             user_liked_count=user_count_info['user_liked_count'],
                             ))
        return data

    @transaction.commit_manually(using=KAIHU_DB)
    def add_customer_manager(self, user_id, department_id_or_obj, end_date, vip_info='', sort_num=0, qq=None, entry_time=None, mobile=None,
                             real_name=None, id_card=None, id_cert=None, des=None, pay_type=0):
        try:
            if not (user_id and department_id_or_obj and end_date):
                return 99800, dict_err.get(99800)

            user = UserBase().get_user_by_id(user_id)
            if not user:
                return 50100, dict_err.get(50100)

            department = department_id_or_obj if isinstance(department_id_or_obj, Department) else DepartmentBase().get_department_by_id(department_id_or_obj)

            if not department:
                return 50101, dict_err.get(50101)

            cm = CustomerManager.objects.create(user_id=user_id, department=department, end_date=end_date, sort_num=sort_num, city_id=department.city_id,
                                                qq=qq, entry_time=entry_time, mobile=mobile, vip_info=vip_info,
                                                real_name=real_name, id_card=id_card, id_cert=id_cert, des=des, pay_type=pay_type)

            # 更新营业部冗余字段
            department.cm_count += 1
            department.save()

            transaction.commit(using=KAIHU_DB)
            return 0, cm
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=KAIHU_DB)
            return 99900, dict_err.get(99900)

    def modify_customer_manager(self, user_id, **kwargs):
        if not user_id:
            return 99800, dict_err.get(99800)

        user = UserBase().get_user_by_id(user_id)
        if not user:
            return 50100, dict_err.get(50100)

        customer_manager = self.get_customer_manager_by_user_id(user_id)
        if not customer_manager:
            return 50102, dict_err.get(50102)

        # 如果修改了营业部，所属城市也要一并修改
        department_id = kwargs.get('department_id')
        if department_id:
            temp = DepartmentBase().get_department_by_id(department_id)
            if not temp:
                return 50101, dict_err.get(50101)
            else:
                kwargs.update({'city_id': temp.city_id})

        try:
            for k, v in kwargs.items():
                setattr(customer_manager, k, v)

            customer_manager.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_customer_managers_by_city_id(self, city_id):
        cms = []
        if city_id:
            cms = list(CustomerManager.objects.select_related('department').filter(city_id=city_id, end_date__gte=datetime.datetime.now(), state=True))
            cms = self.format_customer_managers_for_ajax(cms)

            # 排序方法，按照两个维度，付费类型和赞
            def _cmp(x, y):
                return - 1 if (x['pay_type'] > y['pay_type'] or (x['pay_type'] == y['pay_type'] and x['user_liked_count'] > y['user_liked_count'])) else 1
            cms.sort(cmp=_cmp)
        return cms

    def get_customer_managers_by_department(self, department):
        return CustomerManager.objects.filter(department=department, state=True)

    def get_customer_manager_by_user_id(self, user_id):
        obj = CustomerManager.objects.filter(user_id=user_id)
        if obj:
            return obj[0]
        else:
            return None

    def get_all_customer_managers(self, active=True, state=True):
        objs = CustomerManager.objects.all()
        if active:
            objs = objs.filter(end_date__gte=datetime.datetime.now())

        if state != None:
            objs = objs.filter(state=state)

        return objs

    @transaction.commit_manually(using=KAIHU_DB)
    def remove_customer_manager(self, user_id):
        try:
            obj = self.get_customer_manager_by_user_id(user_id)
            if obj:
                obj.delete()

                # 更新营业部冗余字段
                department = obj.department
                department.cm_count -= 1
                department.save()

                transaction.commit(using=KAIHU_DB)
                return 0, dict_err.get(0)
            else:
                transaction.commit(using=KAIHU_DB)
                return 50100, dict_err.get(50100)
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=KAIHU_DB)
            return 99900, dict_err.get(99900)


class FriendlyLinkBase(object):

    def __init__(self):
        pass

    def format_friendly_links(self, friendly_links):
        cb = CityBase()

        for x in friendly_links:
            x.city = cb.get_city_by_id(x.city_id)

        return friendly_links

    def add_friendly_link(self, name, href, link_type=0, city_id=None, img=None, des=None, sort_num=0):
        try:
            try:
                assert name and href
                if link_type == 0:
                    assert city_id
            except:
                return 99800, dict_err.get(99800)
            obj = FriendlyLink.objects.create(name=name, href=href, city_id=city_id, img=img, link_type=link_type, sort_num=sort_num, des=des)

            # 更新缓存
            self.get_all_friendly_link(must_update_cache=True)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)
        return 0, obj.id

    @cache_required(cache_key='all_friendly_link', expire=0, cache_config=cache.CACHE_STATIC)
    def get_all_friendly_link(self, state=True, must_update_cache=False):
        objects = FriendlyLink.objects.all()
        if state != None:
            objects = objects.filter(state=state)

        return objects

    def get_friendly_link_by_city_id(self, city_id, link_type=(0, )):
        flinks = []
        for flink in (self.get_all_friendly_link()):
            if flink.city_id == city_id and flink.link_type in link_type:
                flinks.append(flink)
        return flinks

    def get_friendly_link_by_id(self, link_id, state=True):
        return self.get_all_friendly_link(state).filter(id=link_id)

    def get_friendly_link_by_name(self, link_name):
        return self.get_all_friendly_link(state=None).filter(name=link_name)

    def get_friendly_link_by_link_type(self, link_type):
        flinks = []
        link_type = link_type if isinstance(link_type, (list, tuple)) else (link_type,)
        for flink in (self.get_all_friendly_link()):
            if flink.link_type in link_type:
                flinks.append(flink)
        return flinks

    def modify_friendly_link(self, link_id, **kwargs):
        if not link_id:
            return 99800, dict_err.get(99800)

        friendly_link = self.get_friendly_link_by_id(link_id, state=None)
        if not friendly_link:
            return 50103, dict_err.get(50103)

        friendly_link = friendly_link[0]

        try:
            for k, v in kwargs.items():
                setattr(friendly_link, k, v)

            friendly_link.save()

            # 更新缓存
            self.get_all_friendly_link(must_update_cache=True)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def remove_friendly_link(self, link_id):
        if not link_id:
            return 99800, dict_err.get(99800)

        friendly_link = self.get_friendly_link_by_id(link_id, state=None)
        if not friendly_link:
            return 50103, dict_err.get(50103)
        friendly_link = friendly_link[0]
        friendly_link.delete()

        self.get_all_friendly_link(must_update_cache=True)
        return 0, dict_err.get(0)

    def search_links_for_admin(self, link_type=0, name=None, city_id=None):

        objs = self.get_all_friendly_link(state=None).filter(link_type=link_type)

        if name:
            objs = objs.filter(name__contains=name)

        if city_id:
            objs = objs.filter(city_id=city_id)

        return objs


class CompanyBase(object):

    """docstring for CompanyBase"""

    def get_companys_by_name(self, company_name):

        companys = []
        if company_name:
            companys = Company.objects.filter(name__contains=company_name)
        return companys

    def get_company_by_id(self, company_id, state=True):
        try:
            ps = dict(id=company_id)
            if state is not None:
                ps.update(dict(state=True))
            return Company.objects.get(**ps)
        except Company.DoesNotExist:
            return None


class ArticleBase(object):

    def get_article_by_id(self, article_id, need_state=True):
        try:
            ps = dict(id=article_id)
            if need_state:
                ps.update(dict(state=True))
            return Article.objects.get(**ps)
        except Article.DoesNotExist:
            return None

    def get_all_articles(self, state=True):
        objs = Article.objects.all()
        if state is not None:
            objs = objs.filter(state=state)

        return objs

    def get_article_by_title(self, title):
        return self.get_all_articles(state=None).filter(title__contains=title)

    def get_articles_by_city_id(self, city_id, order_by=None):
        articles = Article.objects.filter(state=True, city_id=city_id)
        if order_by:
            return articles.order_by(order_by)
        return articles

    def add_article(self, title, content, city_id, department_id=None, sort_num=0):
        if not (title and content and CityBase().get_city_by_id(city_id)):
            return 99800, dict_err.get(99800)

        content = utils.filter_script(content)
        article = Article.objects.create(title=title, content=content, city_id=city_id,
                                         department_id=department_id, sort_num=sort_num)

        return 0, article

    def modify_article(self, article_id, **kwargs):

        if not article_id:
            return 99800, dict_err.get(99800)

        article = self.get_article_by_id(article_id)
        if not article:
            return 50104, dict_err.get(50104)

        try:
            kwargs["content"] = utils.filter_script(kwargs["content"])
            for k, v in kwargs.items():
                setattr(article, k, v)

            article.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def remove_article(self, article_id):
        if not article_id:
            return 99800, dict_err.get(99800)

        article = self.get_article_by_id(article_id)
        if not article:
            return 50104, dict_err.get(50104)

        try:
            article.state = False
            article.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)


class NewsBase(object):

    def get_news_by_id(self, news_id, state=None):
        try:
            ps = dict(id=news_id)
            if state is not None:
                ps.update(dict(state=state))
            return News.objects.get(**ps)
        except News.DoesNotExist:
            return None

    def get_next_news(self, news):
        newses = News.objects.filter(id__lt=news.id)
        if newses:
            return newses[0]

    def get_pre_news(self, news):
        newses = News.objects.filter(id__gt=news.id).order_by("id")
        if newses:
            return newses[0]

    def get_related_newses(self, news):
        return News.objects.filter(id__lt=news.id)[:3]

    def get_all_newses(self, state=True):
        objs = News.objects.all()
        if state is not None:
            objs = objs.filter(state=state)

        return objs


class ExternalCMBase(object):

    """
    """

    def get_external_cm_for_admin(self, name, city_name, department_name, state=0):
        objs = Jfzcm.objects.filter(state=state)

        if name:
            objs = objs.filter(name__contains=name)

        if city_name:
            objs = objs.filter(city_name__contains=city_name)

        if department_name:
            objs = objs.filter(department_name__contains=department_name)

        return objs

    def save_state(self, external_cm_id, state, note=""):
        if not external_cm_id:
            return 99800, dict_err.get(99800)

        obj = Jfzcm.objects.filter(id=external_cm_id)

        if not obj:
            return 99800, dict_err.get(99800)
        obj = obj[0]
        try:
            obj.state = state
            obj.note = note
            obj.save()
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)
