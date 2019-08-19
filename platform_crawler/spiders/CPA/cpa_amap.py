'''
cpa http://youku.union.uc.cn zly
'''
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler import settings

from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from html.parser import HTMLParser
import requests

import json
import time
import os

u = Util()
logger = None


# 解析html文档
class hp(HTMLParser):
    a_text = False

    def __init__(self):
        super(hp, self).__init__()
        self.resArr = []

    def handle_starttag(self, tag, attr):
        if tag == 'td' and len(attr) >= 3 and attr[0][0] == 'height' and attr[1][0] == 'align' and \
                attr[2][0] == 'bgcolor':
            self.a_text = True
        if tag == 'td' and len(attr) >= 2 and attr[0][0] == 'align' and attr[1][0] == 'bgcolor':
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            self.resArr.append(data)


class AmapSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    # pytesseract识别二维码
    def realizeCode(self, vcimgpath):
        img = None
        with open(vcimgpath, 'rb') as f:
            img = f.read()
        vc = u.rc.rk_create(img, 3040)
        logger.info('realizeCode|识别结果：%s' % vc)
        vc_res = vc.get('Result').lower()
        return vc_res, vc, img

    def login(self, ui):
        self.d.get('http://amap.union.uc.cn')
        time.sleep(1)
        inpAccount = self.wait_element(By.ID, 'account')
        inpAccount.clear()
        inpAccount.send_keys(ui['account'])
        inpPassword = self.d.find_element_by_id('password')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = settings.join(settings.IMG_PATH, 'app_imgs', 'amapVerifyCode.png')
        vcodeimg = self.d.find_element_by_id('checkpic')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        lk, vc_obj, im = self.realizeCode(vcimgpath)
        if lk == None or len(lk) == 0:
            logger.error('识别错误')
            return False
        inpVcode = self.d.find_element_by_id('validate_code')
        inpVcode.send_keys(lk)
        time.sleep(5)

        btnLogin = self.d.find_element_by_css_selector('input[value="登 录"]')
        btnLogin.click()

        try:
            self.wait_element(By.CSS_SELECTOR, 'a.topright', wait_time=10)
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies()}
        except Exception as e:
            try:
                text = self.d.find_element_by_css_selector('table div').text
                if text == '验证码错误!':
                    u.rc.rk_report_error(vc_obj.get('Id'))
            finally:
                logger.info('login|step1 error, no login success:%s' % e)
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
            # params = [ui.get('id'), ui.get('account'), ui.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % ui)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    # 从htl中提取select
    def extractSelFromHtml(self):
        self.d.get('http://amap.union.uc.cn/account_manage/mycount.php')
        zdSel = self.wait_element(By.ID, 'zd')
        options = zdSel.find_elements_by_tag_name('option')
        zdDict = {}
        for option in options:
            optval = option.get_attribute('value')
            if not optval:
                continue
            opttxt = option.text
            zdDict[optval] = opttxt

        cpSel = self.d.find_element_by_id('cp')
        options = cpSel.find_elements_by_tag_name('option')
        cpDict = {}
        for option in options:
            optval = option.get_attribute('value')
            if not optval:
                continue
            opttxt = option.text
            cpDict[optval] = opttxt

        logger.info('extractSelFromHtml|success zdDict:%s  cpDict:%s' % (zdDict, cpDict))
        return {
            'zdDict': zdDict,
            'cpDict': cpDict
        }

    # 数据较多，按产品分文件
    def get_data(self, cookie, osd, oed):
        res = self.extractSelFromHtml()

        ckstr = '; '.join(['%s=%s' % (e['name'], e['value']) for e in cookie])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Cookie': ckstr
        }

        for zd in res.get('zdDict'):
            zdtxt = res.get('zdDict').get(zd)
            logger.info('get_data|for zd:%s zdtxt:%s' % (zd, zdtxt))

            for cp in res.get('cpDict'):
                cptxt = res.get('cpDict').get(cp)
                logger.info('get_data|for cp:%s cptxt:%s' % (cp, cptxt))

                url = 'http://amap.union.uc.cn/account_manage/mycount.php?sid=%s&pid=%s&sdate=%s&edate=%s' % (
                zd, cp, osd, oed)
                cres = requests.get(url, headers=headers)
                if cres.status_code != 200:
                    logger.error('get_data|status_code is %s' % cres.status_code)
                    return False

                yk = hp()
                yk.feed(cres.text)
                yk.close()

                tmpres = []
                for idx, val in enumerate(yk.resArr):
                    tmp = {}
                    if idx % 2 == 0:
                        tmp['date'] = val
                    else:
                        tmp['installnum'] = val
                        tmp['zdtxt'] = zdtxt
                        tmp['zdval'] = zd
                        tmp['cpval'] = cp
                        tmp['cptxt'] = cptxt
                        tmpres.append(tmp)

                cptxt = cptxt.replace(' ', '')
                filepath = os.path.join(self.dir_path, '%s_%s_%s_%s.json' % (osd, oed, zdtxt, cptxt))
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(tmpres, ensure_ascii=False))
                logger.info('get_data|写入文件成功%s' % filepath)
        return {'succ': True, 'msg': res}

    def get_img(self, uid, pids, sd, ed):
        Select(self.wait_element(By.ID, 'zd')).select_by_value(uid[0])
        for pid, pname in pids.items():
            Select(self.wait_element(By.ID, 'cp')).select_by_value(pid)
            self.wait_element(By.CLASS_NAME, 'but').click()
            time.sleep(0.5)
            height = self.d.execute_script('return document.body.offsetHeight')
            pic_name = '%s_%s_%s_%s.png' % (uid[1], pname.replace(' ', ''), sd, ed)
            cut_res = cut_img(height, self.dir_path, pic_name)
            if not cut_res.get('succ'):
                logger.error(cut_res)

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

        # 获取上个月到现在每天的数据
        data_list = []
        for start_date, end_date in days:
            try:
                res = self.get_data(cookies, start_date, end_date)
                data_list.append({'sd': start_date, 'ed': end_date, 'data': res.get('msg')})
            except Exception as e:
                logger.error(e, exc_info=1)
        try:
            for i in data_list:
                self.change_date(i.get('sd'), i.get('ed'))
                data = i.get('data')
                for item in data.get('zdDict').items():
                    self.get_img(item, data.get('cpDict'), i.get('sd'), i.get('ed'))
        except Exception as e:
            logger.error(e, exc_info=1)
        finally:
            self.d.quit()

        return {'succ': True}
