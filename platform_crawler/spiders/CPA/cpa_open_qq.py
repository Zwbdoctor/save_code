'''
cpa http://op.open.qq.com/game_channel/list zly
'''
from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import get
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
import json
from selenium.webdriver.common.by import By
from platform_crawler.spiders.get_login_data.login_qq_common import LoginQQCommon
import time
import os

u = Util()
logger = None


class OpenqqSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    def clickToLogin(self):
        self.d.get('http://op.open.qq.com/game_channel/list')
        loginIfr = self.wait_element(By.CSS_SELECTOR, 'iframe#login_frame')
        return loginIfr
    
    # 登录重试
    def runLogin(self, ui):
        lq = LoginQQCommon(ui)
        for e in range(1, 6):
            self.init_browser()
            loginIfr = self.clickToLogin()
            res = lq.login(driver=self.d, loginIfr=loginIfr)
            if res['succ']:
                return res
            else:
                self.d.quit()
        else:
            # 上报无效
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)
            
            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    def getTk(self, skey):
        js_g_tk = r'''
            function getToken(skey) {
                for (var e = skey || "", n = 5381, i = 0, t = e.length; i < t; ++i)
                    n += (n << 5) + e.charCodeAt(i);
                return 2147483647 & n
            }
            return getToken('%s')
        '''
        js_g_tk = js_g_tk % skey
        g_tk = self.d.execute_script(js_g_tk)
        return g_tk
    
    def setDate(self, sd, ed):
        stinp = self.wait_element(By.CSS_SELECTOR, '.input-date-pick')
        stinp.clear()
        stinp.send_keys(sd)
        etinp = self.d.find_element_by_css_selector('#j-time-container .form-col:nth-child(4) .input-date-pick')
        etinp.clear()
        etinp.send_keys(ed)

    # 截图
    def getImg(self, channel_list):
        """截图，并处理图片文件"""
        self.d.get('http://op.open.qq.com/game_channel/atistic')
        self.d.implicitly_wait(10)
        self.wait_element(By.CSS_SELECTOR, '#game-data-table td')
        try:
            mths, dates = u.make_dates(ys=None, ms=None, ye=None, me=None)
            for sd, ed in dates:
                self.setDate(sd, ed)
                for channel in channel_list:
                    self.d.execute_script('document.documentElement.scrollTop=0')
                    self.d.find_element_by_xpath('//*[@class="ui-select"]/a').click()
                    time.sleep(0.5)
                    self.d.find_element_by_xpath('//*[@class="ui-select"]//li[@data-value="%s"]/a' % channel.get('channel_id')).click()
                    searchbtn = self.d.find_element_by_css_selector('.j-main-search')
                    searchbtn.click()
                    self.d.implicitly_wait(15)
                    self.wait_element(By.CSS_SELECTOR, '#game-data-table td')

                    pic_name = '%s_%s_%s.png' % (channel.get('channel_name'), sd, ed)
                    time.sleep(2)       # 等待数据完整之后再计算整个高度
                    height = self.d.execute_script(r'''
                        var stys = window.getComputedStyle(document.body);
                        var pt = parseFloat(stys.paddingTop.replace('px', ''));
                        var pb = parseFloat(stys.paddingBottom.replace('px', ''));
                        return document.body.offsetHeight + pt + pb
                    ''')
                    cut_res = cut_img(height, self.dir_path, pic_name)
                    if not cut_res['succ']:
                        logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
                    logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
                    time.sleep(2)
            else:
                return {'succ': True, 'msg': 'img got success'}
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}

    def get_channels(self, cookie, v_g_tk):
        headers = {
            'Accept': '*/*',
            'Cookie': cookie,
            'Referer': 'https://op.open.qq.com/game_channel/atistic',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        url = "https://op.open.qq.com/game_channel/info"
        querystring = {"g_tk": v_g_tk, "act": "all"}
        channel_id = get(url, params=querystring, headers=headers)
        if not channel_id.get('is_success'):
            return {'succ': False, 'data': "{'msg': 'detail msg like this: %s'}" % channel_id.get('msg')}
        channel_id = channel_id.get('msg').json()
        return {'succ': True, 'channel_ids': channel_id.get('data')}

    def get_data(self, cookie, osd, oed, v_g_tk, cid):
        headers = {
            'Accept': '*/*',
            'cookie': cookie,
            'referer': 'http://op.open.qq.com/game_channel/atistic',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        url = "https://op.open.qq.com/game_channel/statis_get"
        querystring = {"channel_id": cid.get('channel_id'), "g_tk": v_g_tk, "begintime": osd.replace('-', ''),
                       "endtime": oed.replace('-', '')}
        statisres = get(url, params=querystring, headers=headers)
        if statisres['msg'].status_code != 200:
            return {'succ': False, 'data': {'msg': 'detail status_code not 200'}}
        statisres = statisres.get('msg').json()
        if statisres['ret'] != 0:
            logger.info('url:%s, header:%s, detailres:%s' % (url, headers, statisres))
            return {'succ': False, 'data': {'msg': 'detail data error'}}
        if len(statisres['data']) == 0:
            logger.info('url:%s, header:%s, detailres:%s' % (url, headers, statisres))
            return {'succ': True, 'data': 'no data'}
        return {'succ': True, 'data': statisres}

    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)

        # 登陆
        login_res = self.runLogin(ui)
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')

        v_g_tk = None
        for ck in cookies:
            if ck['name'] == 'skey':
                v_g_tk = self.getTk(ck['value'])
                break
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])

        channel_list = self.get_channels(cookie, v_g_tk)
        if not channel_list.get('succ'):
            return channel_list

        # 截图
        img_res = self.getImg(channel_list.get('channel_ids'))
        if not img_res.get("succ"):
            return img_res

        # 获取上个月到现在每天的数据
        res_list = []
        for channel in channel_list.get('channel_ids'):
            for start_date, end_date in days:
                res = self.get_data(cookie, start_date, end_date, v_g_tk, channel)
                if not res.get('succ'):
                    return {'succ': False, 'msg': res['data']}
                if res.get('data') == 'no data':
                    continue
                res_list.append(1)
                file_name = os.path.join(self.dir_path, '%s_%s_%s.json' % (channel.get('channel_name'), start_date, end_date))
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(res.get('data'), f)
                time.sleep(0.25)
        if len(res_list) == 0:
            return {'succ': True, 'msg': 'no data'}

        return {'succ': True}

