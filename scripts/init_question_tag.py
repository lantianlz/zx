# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


def init_question_tag():
    from www.question.models import QuestionType, Tag
    # Tag.objects.all().delete()
    datas = [
        (u'股票', [
            [u'大盘走势', u'dpzs', True, u'http://img0.zhixuan.com/topic_dpzs.jpg', u'''<p>大盘：是指沪市的“上证综合指数”和深市的“深证成份股指数”的股票。</p>
<p>上证综指和深证成指是运用统计学中的指数方法编制而成的，反映沪深股市总体价格变动和走势的指标。</p>
<p>大盘走势可理解为沪深股市走势。</p>
            '''],
            [u'个股分析', u'ggfx', True, u'http://img0.zhixuan.com/topic_ggfx.jpg', u'个股分析指对上市公司发行的股票进行分析，一般分为技术面和基本面分析。'],
            [u'行业分析', u'hyfx', True, u'http://img0.zhixuan.com/topic_hyfx.jpg',
                u'行业分析是指根据经济学原理，综合应用统计学、计量经济学等分析工具对行业经济的运行状况、产品生产、销售、消费、技术、行业竞争力、市场竞争格局、行业政策等行业要素进行深入的分析，从而发现行业运行的内在经济规律，进而进一步预测未来行业发展的趋势。'],
            [u'宏观经济', u'hgjj', True, u'http://img0.zhixuan.com/topic_hgjj.jpg', u'宏观经济指总量经济活动，即国民经济的总体活动。'],
            [u'投资策略', u'tzcl', True, u'http://img0.zhixuan.com/topic_tzcl.jpg', u'投资策略指对投资资产根据不同需求和风险承受能力进行的安排、配制。包括选择股票、债券、商品期货及不动产品种、配制投资资产比例、安排投资周期等内容。'],
            [u'海南股', u'hng', False, u'http://img0.zhixuan.com/topic_hng.jpg', u'注册地或者实际主要经营地在海南的上市公司。'],
            [u'博彩概念股', u'bcgng', False, u'http://img0.zhixuan.com/topic_bcgng.jpg', u'通过互联网，手机APP等渠道销售彩票的上市公司。'],
        ]),
        (u'债券', [
            [u'债券分析', u'zqfx', True, u'http://img0.zhixuan.com/topic_zqfx.jpg', u'对在沪深交易所（不包含银行间市场）发行的债券进行分析，其债券种类包括国债，企业，公司债，可转债等。'],
            [u'正回购', u'zhg', True, u'http://img0.zhixuan.com/topic_zhg.jpg', u'债券持有人（正回购方）将债券质押而获得资金使用权，到约定的时间还本并支付一定的利息，从而“赎回”债券。这个操作即为正回购，正回购可以进行套作，承担债券价格及息差的风险，赚取超额收益。'],
            [u'可转债', u'kzz', True, u'http://img0.zhixuan.com/topic_kzz.jpg', u'可转换债券是债券的一种，它可以转换为债券发行公司的股票，通常具有较低的票面利率。从本质上讲，可转换债券是在发行公司债券的基础上，附加了一份期权，并允许购买人在规定的时间范围内将其购买的债券转换成指定公司的股票。'],
        ]),
        (u'期货', [
            [u'商品期货', u'spqh', True, u'http://img0.zhixuan.com/topic_spqh.jpg',
                u'商品期货是指标的物为实物商品的期货合约。国内的商品期货交易所有大连商品交易所，郑州商品交易所，上海商品交易所。交易品种有螺纹、热卷、线材、铜、铝、锌、铅、天然橡胶、燃油、黄金、钢材、白银、大豆、豆粕、豆油、塑料、棕榈油、玉米、PVC、焦炭、焦煤、铁矿石、纤板、pp合约、鸡蛋、胶板、小麦、棉花、白糖、PTA、菜籽油、早籼稻、甲醇、玻璃、菜籽、菜粕等。'],
            [u'股指期货', u'gzqh', True, u'http://img0.zhixuan.com/topic_gzqh.jpg', u'国内的股指期货目前只有中金所的沪深300指数期货，以沪深300指数为标的物的期货。双方交易的是一定期限后的沪深300指数合约，通过现金结算差价来进行交割。'],
            [u'国债期货', u'guozqh', True, u'http://img0.zhixuan.com/topic_guozqh.jpg', u'国债期货作为利率期货的一个主要品种，是指买卖双方通过有组织的交易场所，约定在未来特定时间，按预先确定的价格和数量进行券款交收的国债交易方式，目前国内的国债期货交易品种有中金所的5年期国债期货合约。'],
        ]),
        (u'期权', [
            [u'个股期权', u'ggqq', True, u'http://img0.zhixuan.com/topic_ggqq.jpg',
                u'期权是交易双方关于未来买卖权利达成的合约。就个股期权来说，期权的买方（权利方）通过向卖方（义务方）支付一定的费用（权利金），获得一种权利，即有权在约定的时间以约定的价格向期权卖方买入或卖出约定数量的特定股票或ETF。当然，买方（权利方）也可以选择放弃行使权利。如果买方决定行使权利，卖方就有义务配合。'],
        ]),
        (u'其他', [
            [u'股票账户', u'gpzh', True, u'http://img0.zhixuan.com/topic_gpzh.jpg', u'本话题包括但不限于股票开户及转户，融资融券开户，交易佣金，行情及交易软件等股票相关的讨论。'],
            [u'期货账户', u'qhzh', True, u'http://img0.zhixuan.com/topic_qhzh.jpg', u'本话题包括但不限于商品期货开户，金融期货开户（股指期货，国债期货），交易佣金，行情及交易软件等期货相关的讨论。'],
            [u'理财咨询', u'lczx', True, u'http://img0.zhixuan.com/topic_lczx.jpg', u'本话题包括但不限于银行理财产品，P2P理财产品，信托理财产品，券商资管理财产品，互联网“宝宝”类理财产品等理财相关的讨论。'],
        ]),
    ]
    for data in datas:
        qt = QuestionType.objects.get(name=data[0])
        for tag in data[1]:
            try:
                tag_obj = Tag.objects.get(name=tag[0])
                tag_obj.img = tag[3]
                tag_obj.des = tag[4]
                tag_obj.domain = tag[1]
                tag_obj.save()
            except Tag.DoesNotExist:
                Tag.objects.create(name=tag[0], domain=tag[1], question_type=qt, is_show=tag[2], img=tag[3], des=tag[4])
    print 'ok'


if __name__ == '__main__':
    init_question_tag()
