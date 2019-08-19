'''
cpa http://cpbi.ijinshan.com zly
    update v2  >>>> add model:  cut_img        --- zwb
'''
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.post_res import post_res
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import IMG_PATH, join

import json
from selenium.webdriver.common.by import By
import time

u = Util()
logger = None


class LieBaoSpider(TaskProcess):
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
        self.d.get('http://cpbi.ijinshan.com')
        time.sleep(1)
        inpAccount = self.wait_element(By.CSS_SELECTOR, '#username')
        inpAccount.clear()
        inpAccount.send_keys(ui['account'])
        time.sleep(1)
        inpPassword = self.d.find_element_by_css_selector('input[name="password"]')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = join(IMG_PATH, 'app_imgs', 'liebaoVerifyCode.png')
        vcodeimg = self.d.find_element_by_id('code_img')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        lk, lk_obj, im = self.realizeCode(vcimgpath)
        if lk == None or len(lk) == 0:
            logger.error('识别错误')
            return False
        inpVcode = self.d.find_element_by_id('checkcode')
        inpVcode.send_keys(lk)
        time.sleep(3)

        # time.sleep(5)

        try:
            btnLoginBtn = self.wait_element(By.CSS_SELECTOR, '.login_submit', wait_time=3)
            btnLoginBtn.click()
        except Exception as e:
            try:
                text = self.d.find_element_by_id('err_checkcode').text
                if text == '验证码错误':
                    logger.info('login|step1 error:验证码错误')
                    u.rc.rk_report_error(lk_obj.get('Id'))
            finally:
                return False

        try:
            btnLogout = self.wait_element(By.CSS_SELECTOR, 'a[href="?a=logout"]', wait_time=10)
            logger.info('login|succ, cookie：%s' % self.d.get_cookies())
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies()}
        except Exception as e:
            logger.info('login|step2 error:没有登录成功')
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
            params = [ui.get('id'), ui.get('account'), ui.get('platform'), None,
                      False]
            if not post_res(*params):
                logger.error('----------useless account! Post result failed!')
            else:
                logger.info('useless account!(%s) Post success!' % ui)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    # 从页面中提取select组合
    def extractSel(self):
        self.d.get('http://cpbi.ijinshan.com')
        selapp = self.wait_element(By.CSS_SELECTOR, 'select[name="app"]')
        options = selapp.find_elements_by_tag_name('option')
        appDict = {}
        for option in options:
            appDict[option.get_attribute('value')] = option.text
        rdType = self.d.find_elements_by_css_selector('.contc form li:nth-child(4) label')
        typeDict = {}
        for rd in rdType:
            if rd.text == '合计':
                continue
            typeDict[rd.find_element_by_css_selector('input[name="type"]').get_attribute('value')] = rd.text
        logger.info('extractSel| appDict:%s typeDict:%s' % (appDict, typeDict))
        return {
            'appDict': appDict,
            'typeDict': typeDict
        }

    # cookie转化为str
    def geneStr(self, cookie):
        resstr = ''
        for ck in cookie:
            resstr = resstr + ck.get('name') + '=' + ck.get('value') + '; '
        logger.info('geneStr|cookie str:%s' % resstr)
        return resstr

    # 抓取两个部分数据
    def getData(self, cookie, osd, oed):
        ckstr = self.geneStr(cookie)
        esres = self.extractSel()
        logger.info('getData|extractSel: %s' % esres)

        for app in esres.get('appDict'):
            appName = esres.get('appDict').get(app)
            for tp in esres.get('typeDict'):
                tpName = esres.get('typeDict').get(tp)

                url = 'http://cpbi.ijinshan.com/?begin=%s&app=%s&end=%s&type=%s&c=user&a=' % (osd, app, oed, tp)
                self.d.get(url)

                self.wait_element(By.CSS_SELECTOR, 'tr.thead td')
                theadtds = self.d.find_elements_by_css_selector('tr.thead td')
                channels = []
                for theadtd in theadtds:
                    if theadtd.text == '日期' or theadtd.text == '每日激活量':
                        continue
                    channels.append(theadtd.text)
                logger.info('getData|列表渠道：%s', channels)

                dataths = self.d.find_elements_by_css_selector('tr[style="background: #fff"]')
                datas = []
                for datath in dataths:
                    rowtds = datath.find_elements_by_tag_name('td')
                    if len(rowtds) != 4:
                        continue
                    tmp = {}
                    tmp['date'] = rowtds[0].text
                    tmp['dayActivate'] = rowtds[1].text
                    tmp[channels[0]] = rowtds[2].text
                    tmp[channels[1]] = rowtds[3].text
                    datas.append(tmp)

                dat = {'datas': datas, 'channels': channels}
                filepath = join(self.dir_path, '%s_%s_%s_%s.json' % (osd, oed, appName, tpName))
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(dat, ensure_ascii=False))
                logger.info('getData|写入文件成功：%s' % filepath)
        return {'succ': True, 'data': {'appDict': esres.get('appDict'), 'typeDict': esres.get('typeDict')}}

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
                res = self.getData(cookies, start_date, end_date)
                if not res:
                    logger.error('getData|error')
                    return
                data_list.append({'sd': start_date, 'ed': end_date, 'data': res.get('data')})
            except Exception as e:
                logger.error(e)

        try:
            for e in data_list:
                self.get_img(e.get('sd'), e.get('ed'), e.get('data'))
        except Exception as e:
            logger.error(e, exc_info=1)
        finally:
            self.d.quit()

        return {'succ': True}

    def get_img(self, sd, ed, data):
        for k, v in data.get('appDict').items():
            for i, s in data.get('typeDict').items():
                url = 'http://cpbi.ijinshan.com/?begin=%s&app=%s&end=%s&type=%s&c=user&a=' % (sd, k, ed, i)
                self.d.get(url)
                try:
                    self.d.execute_script("document.querySelector('#bar_1').click()")
                except Exception:
                    pass
                self.d.execute_script('document.documentElement.scrollTop=0')
                pic_name = '%s_%s_%s_%s.png' % (v, s, sd, ed)
                height = self.d.execute_script("return document.body.offsetHeight")
                cut_res = cut_img(height, self.dir_path, pic_name)
                if not cut_res.get('succ'):
                    logger.warning('got img failed --- named : %s\ndetail msg: %s' % (pic_name, cut_res.get('msg')))
                logger.info('got an img: %s' % pic_name)
                self.d.execute_script('document.documentElement.scrollTop=0')

