'''
cpa http://qimeng.iqiyi.com/ zly
'''
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import join, IMG_PATH, JS_PATH

from selenium.webdriver.common.by import By
from html.parser import HTMLParser
import requests

import time
import json

u = Util()
logger = None
log_name = __name__.split('.')[-1]


# 解析html文档
class hp(HTMLParser):
    a_text = False

    def __init__(self):
        super(hp, self).__init__()
        self.resArr = []

    def handle_starttag(self, tag, attr):
        if tag == 'td':
            self.a_text = True
        if tag == 'td':
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            data = data.replace('\n', '')
            data = data.strip()
            self.resArr.append(data)


class IqiyiSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    def login(self, ui):
        self.d.get('http://qimeng.iqiyi.com/')
        time.sleep(1)
        inpAccount = self.wait_element(By.CSS_SELECTOR, 'input[name="username"]')
        inpAccount.clear()
        inpAccount.send_keys(ui['account'])
        time.sleep(1)
        inpPassword = self.d.find_element_by_css_selector('input[name="password"]')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = join(IMG_PATH, 'app_imgs', 'iqiyiVerifyCode.png')
        vcodeimg = self.d.find_element_by_id('validateCodeImg')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        lk, vc_obj, im = self.realizeCode(vcimgpath)
        if lk == None or len(lk) == 0:
            logger.error('识别错误')
            return False
        inpVcode = self.d.find_element_by_id('validateCode')
        inpVcode.send_keys(lk)
        time.sleep(3)

        # time.sleep(5)

        try:
            btnLoginBtn = self.wait_element(By.CSS_SELECTOR, '.loginBtn:not(.disable)', wait_time=3)
            btnLoginBtn.click()
        except Exception as e:
            logger.info('login|step1 error:验证码错误')
            u.rc.rk_report_error(vc_obj.get('Id'))
            return False

        try:
            navuserinfo = self.wait_element(By.ID, 'nav-userinfo', wait_time=10)
            logger.info('login|succ')
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies()}
        except Exception as e:
            logger.info('login|step2 error:没有登录成功')
            return False

    # 登录重试
    def runLogin(self, ui):
        res = None
        for e in range(1, 6):
            self.init_browser()
            res = self.login(ui)
            if not res:
                self.d.quit()
            else:
                return res
        else:
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            self.result_kwargs.update({'has_data': 0, 'has_pic': 0})
            # if not post_res(*params, **self.result_kwargs):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    def getCidFromHtml(self):
        self.d.get('http://qimeng.iqiyi.com/acti/report')
        try:
            inpCbId = self.d.find_element_by_id('cbId')
            return inpCbId.get_attribute('value')
        except Exception as e:
            logger.error('getActiFromHtml|error: %s' % e)
            return False

    # 获得激活数据
    def getActiData(self, cookies, osd, oed):
        logger.info('getActiData|start osd:%s oed:%s' % (osd, oed))
        cid = self.getCidFromHtml()
        if not cid:
            return False

        ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])
        headers = {
            'Cookie': ckstr,
            'Referer': 'http://qimeng.iqiyi.com/acti/report',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        # 客户端select
        url = "http://qimeng.iqiyi.com/acti/queryClientType?cid=" + cid
        res = requests.post(url, headers=headers)
        if res.status_code != 200:
            logger.error('getActiData|客户端select请求status_code not 200: %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')
        res = json.loads(res)
        clientTypeDict = res.get('results')

        # 渠道select
        url = "http://qimeng.iqiyi.com/channelBusiness/getVendorAndPackage?id=" + cid + "&selectVendorType=2"
        res = requests.post(url, headers=headers)
        if res.status_code != 200:
            logger.error('getActiData|渠道select请求status_code not 200: %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')
        res = json.loads(res)
        vpDict = res.get('results')

        # 渠道包select
        vid = ''
        url = "http://qimeng.iqiyi.com/channelBusiness/getPackageListByCBAndV?cid=" + cid + "&vid=" + vid
        res = requests.post(url, headers=headers)
        if res.status_code != 200:
            logger.error('getActiData|渠道包select请求status_code not 200: %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')
        res = json.loads(res)
        pks = res.get('results')
        logger.info('getActiData|获得pks:%s' % pks)

        for vpd in vpDict:
            vpdId = vpd.get('ID')
            vpdName = vpd.get('NAME')

            for ctd in clientTypeDict:
                ctdId = ctd.get('ID')
                ctdName = ctd.get('NAME')

                for pk in pks:
                    packageId = pk.get('id')
                    packageName = pk.get('package_name')

                    url = "http://qimeng.iqiyi.com/acti/report"
                    data = {
                        'searchType': 'date',
                        'queryDateType': 5,
                        'dataValueStart': osd,
                        'dataValueEnd': oed,
                        'vendor': vpdId,
                        'clientType': ctdId,
                        'packageId': packageId,
                        'cbId': cid,
                        'orderField': '',
                        'orderSort': ''
                    }
                    logger.info('getActiData|for in package request, data:%s' % data)
                    res = requests.post(url, headers=headers, data=data)
                    if res.status_code != 200:
                        logger.error('getActiData|report请求 not 200: %s' % res.status_code)
                        return False

                    # 提取html数据
                    yk = hp()
                    yk.feed(res.text)
                    yk.close()
                    logger.info('getActiData|提取数据%s' % yk.resArr)

                    res = []
                    for idx, val in enumerate(yk.resArr):
                        tmp = {}
                        if idx % 2 == 0:
                            tmp['date'] = val
                        else:
                            tmp['num'] = val
                            tmp['packageId'] = packageId
                            tmp['packageName'] = packageName
                            res.append(tmp)

                            # 写入文件
                    filepath = join(self.dir_path,
                                            '%s_%s_acti_%s_%s_%s.json' % (osd, oed, vpdName, ctdName, packageName))
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(res, ensure_ascii=False))
                    logger.info('getActiData|写入文件成功：%s' % filepath)

        return {'succ': True, 'data': {'clientData': clientTypeDict, 'package': pks, 'vpData': vpDict}}

    # 拉起召回数据
    def getRecallReportData(self, cookies, osd, oed):
        logger.info('getRecallReportData|start osd:%s oed:%s' % (osd, oed))
        ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])
        headers = {
            'Cookie': ckstr,
            'Referer': 'http://qimeng.iqiyi.com/qimengUI/wake/out',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        platforms = ['iPhone', 'GPhone']  # 写在js中不常更改

        # 渠道码请求(可以一次多选)
        url = "http://qimeng.iqiyi.com/qimengnew/recallReport/cbCodeConfigList"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            logger.error('getRecallReportData|status code not 200: %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')
        res = json.loads(res)
        cbCodes = res.get('data')

        # 拉起list请求
        for platform in platforms:
            for cbCode in cbCodes:
                url = 'http://qimeng.iqiyi.com/qimengnew/recallReport/list?groupName=&startDate=%s&endDate=%s&platForm=%s&codeIds=%s&showFiledId=4&limit=200&offset=1' % (
                osd, oed, platform, cbCode.get('colSubChlId'))
                res = requests.get(url, headers=headers)
                if res.status_code != 200:
                    logger.error('getRecallReportData|status code not 200: %s' % res.status_code)
                    return False
                res = res.content.decode('utf-8')
                res = json.loads(res)

                # 写入文件
                filepath = join(self.dir_path, '%s_%s_recallReport_%s_%s.json' % (
                osd, oed, platform, cbCode.get('colSubChlName')))
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(res, ensure_ascii=False))
                logger.info('getRecallReportData|写入文件成功：%s' % filepath)

        return {'succ': True, 'data': {'platform': platforms, 'cCodes': cbCodes}}

    # 抓取两个部分数据
    def get_data(self, cookie, osd, oed):
        # actiData = self.getActiData(cookie, osd, oed)
        # if not actiData:
        #     logger.info('get_data|error getActiData失败')

        recallReportData = self.getRecallReportData(cookie, osd, oed)
        if not recallReportData:
            logger.info('get_data|error getRecallReportData失败')

        # return {'succ': True, 'data': {'activeData': actiData, 'recallData': recallReportData}}
        return {'succ': True, 'data': {'recallData': recallReportData}}

    def ch_act_date(self, sd, ed):
        self.d.execute_script('''document.querySelector("#dataValueStart").value="%s"''' % sd)
        self.d.execute_script('''document.querySelector("#dataValueEnd").value="%s"''' % ed)
        # self.d.execute_script('''document.querySelector('#search_btn').click()''' % ed)

    def ch_recall_date(self, sd, ed):
        # change recall page date
        with open(join(JS_PATH, 'iqiyi.js'), 'r', encoding='utf-8') as f:
            js = f.read()
        js = js % (sd, ed)
        self.d.execute_script(js)

    def get_img_act(self, sd, ed, data):
        vp_list = data.get('vpData')
        for vd in vp_list:
            self.d.execute_script('document.querySelector("#selectType0").value="%s"' % vd.get("ID"))
            for cd in data.get('clientData'):
                self.d.execute_script('document.querySelector("#selectClient").value="%s"' % cd.get("ID"))
                for pd in data.get('package'):
                    self.d.execute_script('''document.querySelector("#selectType1").value="%s"''' % pd.get("id"))
                    time.sleep(0.5)
                    self.wait_element(By.ID, 'search_btn').click()
                    self.d.implicitly_wait(5)
                    pic_name = '%s_%s_%s_%s_%s.png' % (vd.get('NAME'), cd.get('NAME'), pd.get('NAME'), sd, ed)
                    height = self.d.execute_script("return document.body.offsetHeight")
                    cut_res = cut_img(height, self.dir_path, pic_name)
                    if not cut_res.get('succ'):
                        logger.warning('got img failed --- named : %s\ndetail msg: %s' % (pic_name, cut_res.get('msg')))
                        continue
                    logger.info('got an img: %s' % pic_name)

    def get_img_recall(self, sd, ed):
        # Cut recall page image
        pic_name = 'recall_%s_%s.png' % (sd, ed)
        height = self.d.execute_script("return document.body.offsetHeight")
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.warning('got img failed --- named : %s\ndetail msg: %s' % (pic_name, cut_res.get('msg')))
        logger.info('got an img: %s' % pic_name)

    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)

        # 登陆
        login_res = self.runLogin(ui)
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')

        # 获取上个月到现在每天的数据
        data_list = []
        for start_date, end_date in days:
            try:
                res = self.get_data(cookies, start_date, end_date)
                if not res:
                    logger.error('get_data|error')
                    return
                data_list.append({'sd': start_date, 'ed': end_date, 'data': res.get('data')})
            except Exception as e:
                logger.error(e)

        for data in data_list:
            # self.d.get('http://qimeng.iqiyi.com/acti/report')
            # self.ch_act_date(data.get('sd'), data.get('ed'))
            # self.get_img_act(data.get('sd'), data.get('ed'), data.get('data').get('activeData').get('data'))
            self.d.get('http://qimeng.iqiyi.com/qimengUI/wake/out')
            self.ch_recall_date(data.get('sd'), data.get('ed'))
            self.get_img_recall(data.get('sd'), data.get('ed'))

        return {'succ': True}
