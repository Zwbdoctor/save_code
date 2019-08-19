"""
:s#vivian/#sky/# 替换当前行第一个 vivian/ 为 sky/

:%s+/oradata/apras/+/user01/apras1+ （使用+ 来 替换 / ）： /oradata/apras/替换成/user01/apras1/
"""
from platform_crawler.spiders.pylib.get_pwd import get_pwd_encryped
import json
from platform_crawler.utils.post_get import post
from . import class_register
from platform_crawler.settings import BASEDIR, join


ul = [
    {'id': 10221, 'platform': '2345', 'account': 'sc-hhmt_as_yyw', 'password': '2345.com'},
    {'id': 10221, 'platform': 'JRTT', 'account': '3128312067@qq.com', 'password': 'Hhmt123456.'},
    {'id': 10221, 'platform': 'TTX', 'account': 'huihuang_newslite', 'password': '95JTBDRM79'},
    {'id': 10221, 'platform': 'ZYInput', 'account': 'zysrf_lele', 'password': 'lele$$$666'},
    # {'id': 10221, 'platform': 'LZS', 'account': 'icooucom@163.com', 'password': '320714'},
    # {'id': 10221, 'platform': 'SLY', 'account': 'szhuihuang', 'password': '654321', 'date': (2018, 1, 2018, 11)},
    {'id': 10221, 'platform': 'UC', 'account': 'hhmtUCxin', 'password': 'aJ6!Jfa91', 'dataPassword': 'KYKMe4QL'},
    {'id': 1246, 'platform': 'YYBSYH', 'account': '3413974023', 'password': 'lzxw6666', 'dates': (2019, 7, 2019, 7)},
    # {'id': 1246, 'platform': 'qq_finance', 'account': '2382300263', 'password': 'hqq233333', 'dates': (2018, 8, 2018, 8)},
    {'id': 1247, 'platform': 'GDT', 'account': '1992356709', 'password': 'Hhmt123456', 'dates': (2019, 7, 2019, 7)},

    {'id': 1248, 'platform': 'YYBHLCPD', 'account': '2811787242', 'password': 'hhmt!2345@', 'dates': (2019, 7, 2019, 7)},
    # {'id': 1248, 'platform': 'Alios', 'account': 'ginger@btomorrow.cn', 'password': 'Ab123456', 'dates': (2019, 7, 2019, 7)},
    {'id': 1248, 'platform': 'Alios', 'account': 'wangdi@btomorrow.cn', 'password': 'Abc123456', 'dates': (2019, 7, 2019, 7)},
    # {'id': 1248, 'platform': 'aliEx', 'account': 'wangdi@btomorrow.cn', 'password': 'Abc123456', 'dates': (2019, 2, 2019, 2)},
    {'id': 1248, 'platform': 'WIFIKEY', 'account': '3013733157@qq.com', 'password': 'Aabb123', 'dates': (2019, 7, 2019, 7)},
    {'id': 1249, 'platform': 'VIVOSTORE', 'account': 'btomorrow_AD01', 'password': 'hhmt-123456', 'dates': (2019, 6, 2019, 7)},
    {'id': 1249, 'platform': 'OPPOSTORE', 'account': 'kuaikan', 'password': 'kuaikan', 'dates': (2019, 6, 2019, 7)},
    {'id': 1251, 'platform': 'XIAOMISTORE', 'account': '1413520467', 'password': 'gs123456', 'dates': (2019, 6, 2019, 6),
     'loginUrl': 'http://e.qq.com/ads/'},
    {'id': 1252, 'platform': 'SGQD', 'account': 'wuxue06@baidu.com', 'password': 'yoyu1234', 'dates': (2019, 4, 2019, 4)},
    {'id': 12520, 'platform': 'QTT', 'account': '猎豹清理大师01', 'password': 'Ab123456', 'dates': (2019, 7, 2019, 7)},
    {'id': 1253, 'platform': 'BDSJZS', 'account': 'baidu-分发智鸟50-B19KA00385', 'password': 'QWEasd123',
     'loginUrl': 'http://baitong.baidu.com'},
    {'id': 1254, 'platform': 'BDXXL', 'account': '原生-北京智鸟A2A18KA1773', 'password': 'QAZqaz123', 'dates': (2019, 6, 2019, 7)},


    # {'id': 169438, 'platform': 'HUAWEISTORE', 'account': 'dlr@btomorrow.cn', 'password': 'Hhmt123456', 'dates': (2019, 7, 2019, 7)},
    {'id': 1255, 'platform': 'HUAWEISTORE', 'account': 'zhonglijuan@btomorrow.cn', 'password': 'Hhmt123456', 'dates': (2019, 7, 2019, 7)},
    {'id': 23125, 'platform': 'MEIZUSTORE', 'account': '13082812039', 'password': 'Jj2017888', 'dates': (2019, 6, 2019, 7)},
    {'id': 23125, 'platform': 'MEIZUSTORE', 'account': '13161744269', 'password': 'SHAREtimes123', 'dates': (2019, 6, 2019, 7)},
    {'id': 23125, 'platform': 'MEIZUSTORE', 'account': '13715237302', 'password': 'fanshu123', 'dates': (2019, 6, 2019, 7)},
    {'id': 23125, 'platform': 'MEIZUSTORE', 'account': 'haohaozhu2015@flyme.cn', 'password': 'Z0ingZ0iS', 'dates': (2019, 6, 2019, 7)},


    {'id': 1258, 'platform': 'OpenQQ', 'account': '3228769757', 'password': 'hhmt!23456',
     'loginUrl': 'http://op.open.qq.com/game_channel/list'},
    {'id': 1259, 'platform': 'QQ', 'account': 'shenchouhuihuangmingtian', 'password': 'shenchouhuihuangmingtian',
     'loginUrl': 'http://unicorn.wcd.qq.com/login.html', 'dates': (2019, 6, 2019, 6)},
    {'id': 1260, 'platform': '360', 'account': 'zhushou_8967002', 'password': '000000',
     'loginUrl': 'http://channel.360.cn/'},
    # {'id': 1261, 'platform': '360A', 'account': 'lindukeji', 'password': 'ld123456',
    #  'loginUrl': 'http://channel.360.cn/'},
    # {'id': 1262, 'platform': '360A', 'account': '13528705592', 'password': 'ld123456',
    #  'loginUrl': 'http://channel.360.cn/'},
    {'id': 1262, 'platform': '360dsp', 'account': 'lindudsp', 'password': '000000',
     'loginUrl': 'http://channel.360.cn/'},
    {'id': 1262, 'platform': '360A', 'account': 'hhmtys', 'password': 'hhmt1234',
     'loginUrl': 'http://channel.360.cn/'},
    {'id': 1263, 'platform': 'SGBrowser', 'account': '光速网络', 'password': '68vUZ0',
     'loginUrl': 'http://tg.app.sogou.com/'},
    {'id': 1263, 'platform': 'SGBrowser', 'account': '辉煌明天', 'password': 'tkk6no',
     'loginUrl': 'http://tg.app.sogou.com/'},
    # {'id': 1263, 'platform': 'SGSJZS', 'account': '仙果广告2', 'password': '0vD323',
    #  'loginUrl': 'http://tg.app.sogou.com/'},
    {'id': 1263, 'platform': 'SGSJZS', 'account': '辉煌明天', 'password': '64FwU6',
     'loginUrl': 'http://tg.app.sogou.com/'},
    {'id': 1264, 'platform': 'TaoBao', 'account': 'zhaoxunfu@btomorrow.cn', 'password': 'hhmt12345',
     'loginUrl': 'http://wcp.taobao.com'},
    # {'id': 1264, 'platform': 'TaoBao', 'account': 'fulton@btomorrow.cn', 'password': 'hhmt@12345',
    #  'loginUrl': 'http://wcp.taobao.com'},
    {'id': 1266, 'platform': 'YouKu', 'account': 'yk_huihuangmt', 'password': '`zrh6Y3Lh@1',
     'dataPassword': 'J6cMajcz', 'loginUrl': 'http://youku.union.uc.cn'},
    {'id': 1267, 'platform': 'Iqiyi', 'account': '辉煌明天', 'password': 'huihuang0328',
     'loginUrl': 'http://qimeng.iqiyi.com'},
    # {'id': 1267, 'platform': '37', 'account': 'szxw10632', 'password': '37shouyou', 'loginUrl': 'http://union.m.37.com/user/login'},
    {'id': 1267, 'platform': '37', 'account': 'xwhd10336', 'password': '37shouyou', 'loginUrl': 'http://union.m.37.com/user/login'},
    {'id': 1267, 'platform': 'GaoDe', 'account': 'huihuang', 'password': 'hh1234***12', 'loginUrl': 'http://amap.union.uc.cn/'},
    {'id': 1267, 'platform': 'KWYY', 'account': 'yilikeji', 'password': 'yilijwl', 'loginUrl': 'http://xkwlm.koowo.com/admin/login'},
    {'id': 1267, 'platform': 'LieBao', 'account': 'shenhuihuang', 'password': 'cmcm1234', 'loginUrl': 'http://cpbi.ijinshan.com'},
    {'id': 1267, 'platform': 'TXWX', 'account': '3592806049', 'password': 'hhmt123456', 'loginUrl': 'https://s.qq.com'},
    {'id': 1267, 'platform': 'TXWX', 'account': '3420660296', 'password': 'hhmt123456', 'loginUrl': 'https://s.qq.com'},
    {'id': 1267, 'platform': 'XSDQ', 'account': 'huihuang@ishugui.com', 'password': '123456', 'loginUrl': 'http://cp.chaohuida.com:9097/manage/user/login.html'},
    {'id': 2341, 'platform': 'OPPOSTORE', 'account': 'Q-杭州煎饼网络技术有限公司-信息流', 'password': 'kjdt123', 'dates': (2019, 2, 2019, 2)},
    {'id': 2341, 'platform': 'DC', 'account': 'DU282', 'password': '123456'},    # , 'dates': (2019, 2, 2019, 2)},
    {'id': 2341, 'platform': 'ZY', 'account': 'hsdlzy11@163.com', 'password': 'hhmt123456', 'dates': (2019, 4, 2019, 4)},
    {'id': 2341, 'platform': 'LH', 'account': 'lianshangdu1@sina.com', 'password': 'hhmt123456', 'dates': (2019, 7, 2019, 7)},
    {'id': 2341, 'platform': 'TA', 'account': '2702600249@qq.com', 'password': 'hksptuia2019', 'dates': (2019, 4, 2019, 4)},


]


def send_params_to_parse(platform, account):
    data = {"platform": platform, 'account': account}
    test_url = 'http://erp.btomorrow.cn/adminjson/ERP_AnalysisCPA'
    ret = post(test_url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, timeout=60)
    if not ret.get('is_success'):
        print(ret.get('msg').text)
    print(f'parser | {ret.get("msg").text}')


def acc_list():
    with open(join(BASEDIR, 'oppo_acct.json'), 'r', encoding='utf-8') as f:
        rd = json.load(f)
    # u = [{'id': num, 'platform': item[0], 'account': item[1], 'password': item[2]} for num, item in enumerate(rd, 1001)]
    u = [{'id': num, 'platform': i['platform'], 'account': i['account'], 'password': i['password'], 'dates': (2019, 7, 2019, 7)}
         for num, i in enumerate(rd, 1001)]
    # print(u)
    return u


def run():
    # ul = acc_list()
    for ui in ul:
        if ui['platform'] in ['YYBHLCPD']:
            print("ui:%s" % ui)
            ui['password'] = get_pwd_encryped(ui.get('password'))
            ap = class_register(ui.get('platform'))(ui, get_img=True)
            ap.run_task(ui)
            del(ap)
            # send_params_to_parse(ui.get('platform'), ui.get('account'))


if __name__ == '__main__':
    run()
    # send_params_to_parse('QQ', 'shenchouhuihuangmingtian')
    # acc_list()
