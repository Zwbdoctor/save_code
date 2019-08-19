'''
cpa http://youku.union.uc.cn zly
'''
from platform_crawler.utils.utils import Util
import requests
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
# from platform_crawler.settings import IMG_PATH, join

import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
import os
import re
from html.parser import HTMLParser

u = Util()
logger = None


# 解析html文档
class hp(HTMLParser):
    a_text = False

    def __init__(self):
        super(hp, self).__init__()
        self.resArr = []

    def handle_starttag(self, tag, attr):
        if tag == 'td' and len(attr) >= 3 and attr[0][0] == 'height' and attr[1][0] == 'align' \
                and attr[2][0] == 'bgcolor':
            self.a_text = True
        if tag == 'td' and len(attr) >= 2 and attr[0][0] == 'align' and attr[1][0] == 'bgcolor':
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            self.resArr.append(data)


class YouKuSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    # pytesseract识别二维码
    def realizeCode(self, vcimgpath):
        with open(vcimgpath, 'rb') as f:
            img = f.read()
        vc = u.rc.rk_create(img, 3040)
        logger.info('realizeCode|识别结果：%s' % vc)
        vc_res = vc.get('Result').lower()
        return vc_res, vc, img

    def login(self, ui):
        self.d.get('http://youku.union.uc.cn/')
        time.sleep(1)
        inpAccount = self.wait_element(By.ID, 'account')
        inpAccount.clear()
        inpAccount.send_keys(ui['account'])
        inpPassword = self.d.find_element_by_id('password')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = os.path.join(os.path.dirname(__file__), '../../imgs/app_imgs/youkuVerifyCode.png')
        vcodeimg = self.d.find_element_by_id('checkpic')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        lk, lk_obj, im = self.realizeCode(vcimgpath)
        if lk == None or len(lk) == 0:
            logger.error('识别错误')
            return False
        inpVcode = self.d.find_element_by_id('validate_code')
        inpVcode.send_keys(lk)
        # time.sleep(5)

        btnLogin = self.d.find_element_by_css_selector('input[value="登 录"]')
        btnLogin.click()

        try:
            inpDataPass = self.wait_element(By.CSS_SELECTOR, 'input[name="datapassword"]', wait_time=10)
            logger.info('login|datapassword found')
            inpDataPass.send_keys(ui['dataPassword'])
            inpDpSubmit = self.d.find_element_by_css_selector('.account-succ input[value="确定"]')
            inpDpSubmit.click()
        except Exception as e:
            try:
                text = self.d.find_elements_by_css_selector('table div').text
                if '验证码错误' in text:
                    u.rc.rk_report_error(lk_obj.get('Id'))
                    logger.info('login|step1 error:%s' % e)
            finally:
                return False

        try:
            selZd = self.wait_element(By.ID, 'zd', wait_time=10)
            opts = selZd.find_elements_by_tag_name('option')
            zdDict = {}
            for opt in opts:
                if re.search(r'废弃|作弊|综合数据', opt.text):
                    continue
                zdDict[opt.get_attribute('value')] = opt.text
            logger.info('login|succ:%s' % zdDict)
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies(), 'zdDict': zdDict}
        except Exception as e:
            logger.info('login|step2 error:%s' % e)
            return False

    # 登录重试
    def runLogin(self, ui):
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
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    def get_data_byzd(self, cookie, zd, zdname, osd, oed):
        logger.info('get_data_byzd|zd:%s osd:%s oed:%s' % (zdname, osd, oed))
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        url = 'http://youku.union.uc.cn/account_manage/mycount.php'
        headers = {
            'Cookie': cookie,
            'Host': 'youku.union.uc.cn',
            'Referer': 'http://youku.union.uc.cn/account_manage/mycount.php',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        data = {
            'pid': 0,
            'sid': zd,
            'sdate': osd,
            'edate': oed
        }
        res = requests.post(url, headers=headers, data=data)
        if res.status_code != 200:
            logger.info('get_data_byzd|status code no 200')
            return False

        hpIns = hp()
        yk = hp()
        yk.feed(res.text)
        yk.close()

        res = []
        for idx, val in enumerate(yk.resArr):
            if idx % 2 == 0:
                tmp = {}
                tmp['date'] = val
            else:
                tmp['installnum'] = val
                tmp['sid'] = zd
                tmp['sname'] = zdname
                res.append(tmp)
        return res

    # 数据较多，按产品分文件
    def get_data(self, cookie, zdDict, osd, oed):
        allres = []
        filepath = os.path.join(self.dir_path, '%s_%s.json' % (osd, oed))
        for zd in zdDict:
            res = self.get_data_byzd(cookie, zd, zdDict.get(zd), osd, oed)
            if not res:
                logger.error('get_data|error 1')
                return False
            allres = allres + res

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(allres, ensure_ascii=False))
        return True

    def get_img(self, zdict, sd, ed):
        for k, v in zdict.items():
            s = Select(self.wait_element(By.ID, 'zd'))
            s.select_by_value(k)
            self.wait_element(By.CLASS_NAME, 'but').click()
            time.sleep(0.5)
            pic_name = '%s_%s_%s.png' % (v, sd, ed)
            cut_res = cut_img(None, self.dir_path, pic_name)
            if not cut_res.get('succ'):
                logger.error(cut_res)
            logger.info('got an pic : %s' % pic_name)

    def change_date(self, sd, ed):
        self.wait_element(By.ID, 'sdate').clear()
        self.wait_element(By.ID, 'sdate').send_keys(sd)
        self.wait_element(By.ID, 'edate').clear()
        self.wait_element(By.ID, 'edate').send_keys(ed)
        self.wait_element(By.CLASS_NAME, 'but').click()

    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)

        # 登陆
        login_res = self.runLogin(ui)
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')
        zdDict = login_res.get('zdDict')

        # 获取上个月到现在每天的数据
        for start_date, end_date in days:
            try:
                res = self.get_data(cookies, zdDict, start_date, end_date)
            except Exception as e:
                logger.error(e)

        for sd, ed in days:
            try:
                self.change_date(sd, ed)
                self.get_img(zdDict, sd, ed)
            except Exception as e:
                logger.error(e)

        return {'succ': True}

