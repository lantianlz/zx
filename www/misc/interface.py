# -*- coding: utf-8 -*-


from django.conf import settings
from www.misc import consts
from www.misc.decorators import cache_required


dict_err = {
}
dict_err.update(consts.G_DICT_ERROR)


@cache_required(cache_key='sitemap', expire=1800)
def generate_sitemap(must_update_cache=False):
    from www.question.interface import TopicBase
    from www.question.models import Question

    data = ''
    for question in Question.objects.filter(state=True).order_by('-id'):
        data += '%s/question/%s\n' % (settings.MAIN_DOMAIN, question.id)

    for topic in TopicBase().get_all_topics_for_show():
        data += '%s/topic/%s\n' % (settings.MAIN_DOMAIN, topic.domain)

    return data
