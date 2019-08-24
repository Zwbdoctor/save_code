MSG_BASE_MODULE_PATH = 'platform_crawler.spiders.MessageStream'
CPA_BASE_MODULE_PATH = 'platform_crawler.spiders.CPA'
__all__ = [
    'apis', 'configs', 'imgs', 'spiders', 'utils', 'settings'
]


def rebuild_path(left_path, module_name):
    module, class_name = module_name.split('.')
    path = '%s.%s' % (left_path, module)
    return path, class_name


def import_source(path, class_name):
    import importlib
    module = importlib.import_module(path)
    cls = getattr(module, class_name)
    return cls


def class_register(class_key=None):
    spider_type = {
        # ------------  MSG  -------------
        'WIFIKEY': rebuild_path(MSG_BASE_MODULE_PATH, 'wifi_spider.WifiSpider'),
        'YYBSYH': rebuild_path(MSG_BASE_MODULE_PATH, 'app_treasure.AppTreasure'),
        'YYBHLCPD': rebuild_path(MSG_BASE_MODULE_PATH, 'app_treasure_huanliang.AppTreasureHL'),
        'Alios': rebuild_path(MSG_BASE_MODULE_PATH, 'aliSpider.AliyunSpider'),
        'GDT': rebuild_path(MSG_BASE_MODULE_PATH, 'app_treasure_gdt.AppTreasureGDT'),
        'VIVOSTORE': rebuild_path(MSG_BASE_MODULE_PATH, 'vivo_spider.VivoSpider'),
        'OPPOSTORE': rebuild_path(MSG_BASE_MODULE_PATH, 'oppo_spider.OppoSpider'),
        'XIAOMISTORE': rebuild_path(MSG_BASE_MODULE_PATH, 'xiaomi_spider.XiaoMiSpider'),
        'SGQD': rebuild_path(MSG_BASE_MODULE_PATH, 'sougou_spider.SouGouSpider'),
        'QTT': rebuild_path(MSG_BASE_MODULE_PATH, 'qutoutiao_spider.QuTouTiaoSpider'),
        'BDSJZS': rebuild_path(MSG_BASE_MODULE_PATH, 'baidu_phone_spider.BaiduPhoneSpider'),
        'BDXXL': rebuild_path(MSG_BASE_MODULE_PATH, 'baidu_message_stream.BaiduMessageSpider'),
        'HUAWEISTORE': rebuild_path(MSG_BASE_MODULE_PATH, 'huawei_spider.HuaWeiSpider'),
        'MEIZUSTORE': rebuild_path(MSG_BASE_MODULE_PATH, 'meizu_spider.MeizuSpider'),
        'JRTT': rebuild_path(MSG_BASE_MODULE_PATH, 'jinritoutiao_spider.JinRiTouTiaoSpider'),
        'ZY': rebuild_path(MSG_BASE_MODULE_PATH, 'zuiyou.ZuiYouSpider'),
        'TA': rebuild_path(MSG_BASE_MODULE_PATH, 'tuia_spider.TuiASpider'),
        'LH': rebuild_path(MSG_BASE_MODULE_PATH, 'liehu_spider.LieHuSpider'),
        'KS': rebuild_path(MSG_BASE_MODULE_PATH, 'kuaishou_spider.KuaiShouSpider'),
        # ------------  CPA  -------------
        '360A': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_channel_360_zong.Channel360zong'),
        '360': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_channel_360_fen.Channel360fen'),
        'SGBrowser': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_app_sogou.SogouSpider'),
        'SGSJZS': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_app_sogou.SogouSpider'),
        'OpenQQ': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_open_qq.OpenqqSpider'),
        'TXWX': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_s_qq.SqqSpider'),
        'TaoBao': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_taobao.TaobaoSpider'),
        'QQ': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_wcd_qq.WcdQQSpider'),
        'Iqiyi': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_iqiyi.IqiyiSpider'),
        'YouKu': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_youku.YouKuSpider'),
        'GaoDe': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_amap.AmapSpider'),
        '37': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_37.Cpa37Spider'),
        'KWYY': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_kwyy.KwyySpider'),
        'XSDQ': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_xsdq.XsdqSpider'),
        'LieBao': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_liebao.LieBaoSpider'),
        'UC': rebuild_path(CPA_BASE_MODULE_PATH, 'uc_spider.UCSpider'),
        'SLY': rebuild_path(CPA_BASE_MODULE_PATH, 'shengleyou_spider.SLYSpider'),
        'ZYInput': rebuild_path(CPA_BASE_MODULE_PATH, 'zhangyushurufa_spider.ZYZSSpider'),
        'TTX': rebuild_path(CPA_BASE_MODULE_PATH, 'toutiao_spider.TouTiaoSpider'),
        '2345': rebuild_path(CPA_BASE_MODULE_PATH, 'browser_2345sys.Browser2345Spider'),
        '360dsp': rebuild_path(CPA_BASE_MODULE_PATH, 'cpa_channel_360_dsp.Cpa360Dsp'),
        'DC': rebuild_path(CPA_BASE_MODULE_PATH, 'dianchuan_spider.DCSpider')
    }
    if class_key:
        return import_source(*spider_type.get(class_key))
    return spider_type
