'''
cpa http://channel.360.cn/ zly
'''
from selenium.webdriver.common.by import By
import json
import time
import os

from platform_crawler.spiders.CPA.cpa_channel_360_fc import Channel360TaskProcess
from platform_crawler.settings import join, IMG_PATH
from platform_crawler.utils.utils import Util

u = Util()


# 360子账号任务类
class Channel360fen(Channel360TaskProcess):
    def __init__(self, data, **kwargs):
        print('360子账号任务类初始化')
        super().__init__(data, **kwargs)

    # 重写登录框逻辑
    def login(self, ui):
        self.d.get('http://channel.360.cn/')
        self.d.implicitly_wait(10)
        loginBtn = self.wait_element(By.CSS_SELECTOR, '._1wpszmp05gC2wm2vtV-s3d>div a:first-child')
        loginBtn.click()
        inpUser = self.wait_element(By.CSS_SELECTOR, 'input[name="username"]')
        inpUser.clear()
        inpUser.send_keys(ui['account'])
        inpPass = self.d.find_element_by_css_selector('input[name="password"]')
        inpPass.clear()
        inpPass.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = join(IMG_PATH, 'app_imgs', 'channel360SonVerifyCode.png')
        vcodeimg = self.d.find_element_by_css_selector('._1wSO9-qM_eUcUq8JnAeHkD img')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        with open(vcimgpath, 'rb') as f:
            im = f.read()
        lkres = u.rc.rk_create(im, '3040')
        lk, lk_id = lkres.get('Result'), lkres.get('Id')
        inpVc = self.d.find_element_by_css_selector('input[name="validate"]')
        inpVc.send_keys(lk)
        time.sleep(2)

        btnLogin = self.d.find_element_by_css_selector('button[type="submit"]')
        btnLogin.click()
        time.sleep(4)

        loginRes = self.isLogin()
        self.logger.info('isLogin:%s' % loginRes)
        if loginRes == False:
            try:
                text = self.d.find_element_by_css_selector('.form-group span').text
                if text == '验证码错误':
                    u.rc.rk_report_error(lk_id.get('Id'))
            finally:
                return {'succ': False, 'msg': 'login fail'}
        else:
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies(), 'appdict': loginRes}

    def getDataByApp(self, app, appname, res_list):
        try:
            channelstr = self.getAppChannelSelList(app)

            for sd, ed in self.dates:
                allDetailList = []  # 单个app所有数据
                page = -1  # 当前页数
                pages = -1  # 总页数
                while page == -1 or page <= pages:
                    if page == -1:
                        page = 1
                    res = self.getAppByPage(app, sd, ed, channelstr, page)
                    if not res:
                        self.logger.error('getAppByPage返回错误')
                        return False

                    allDetailList = allDetailList + res.get('detailList')
                    self.logger.info('allDetailList length:%s' % len(allDetailList))
                    page = page + 1
                    pages = res.get('pages')
                    time.sleep(0.2)

                if not allDetailList:
                    res_list.append(1)
                file_name = os.path.join(self.dir_path, '%s_%s_%s.json' % (sd, ed, appname))
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(allDetailList, ensure_ascii=False))

        except Exception as e:
            self.logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}

    def getData(self, appdict):
        res_list = []
        for app in appdict:
            self.getDataByApp(app, appdict.get(app), res_list)
        if not res_list:
            self.result_kwargs['has_data'] = 0

    def get_img_process(self, app_dict):
        """所有截图流程"""
        for app, app_name in app_dict.items():
            if not self.getAppChannelSelList(app):      # 获取当前app_id
                continue
            self.getImg(app, app_name)
