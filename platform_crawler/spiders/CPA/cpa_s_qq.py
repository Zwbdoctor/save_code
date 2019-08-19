'''
cpa http://s.qq.com zly
'''
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.get_login_data.login_qq_common import LoginQQCommon
from platform_crawler.utils.post_get import post
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import time
import json
import os
import math

u = Util()
logger = None


class SqqSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        self.user_info = user_info
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    def clickToLogin(self):
        self.d.get('https://s.qq.com')
        headerLoginBtn = self.wait_element(By.ID, 'header_login', ec=EC.element_to_be_clickable)
        headerLoginBtn.click()
        loginIfr = self.wait_element(By.CSS_SELECTOR, 'iframe[id="ui.ptlogin"]')
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
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    def setDate(self, sd, ed):
        stinp = self.wait_element(By.CSS_SELECTOR, '#starttime')
        stinp.clear()
        stinp.send_keys(sd)
        etinp = self.d.find_element_by_css_selector('#endtime')
        etinp.clear()
        etinp.send_keys(ed)

    # 截图
    def getImg(self, sd, ed, data):
        """截图，并处理图片文件"""
        self.d.get('https://s.qq.com/tx/data/center.html')
        self.wait_element(By.CSS_SELECTOR, '#dataTable td')
        self.d.execute_script('document.querySelector("#header_noticecontent").remove()')
        try:
            self.setDate(sd, ed)
            for channel in data.get('channelList'):
                ele = self.d.find_element_by_id('qudaoselect')
                qudao_slt = Select(ele)
                qudao_slt.deselect_all()
                qudao_slt.select_by_value(str(channel.get('id')))
                for game in data.get('gameList'):
                    self.d.execute_script("document.querySelector('#gameselect').value = '%s'" % game.get('id'))
                    self.d.execute_script(
                        "document.querySelector('p.search span').textContent = '%s'" % game.get('name'))
                    self.wait_element(By.CSS_SELECTOR, '#querybtn').click()
                    # searchbtn.click()
                    page = 1
                    while True:
                        self.d.execute_script('document.documentElement.scrollTop=0')
                        msg = self.wait_element(By.CSS_SELECTOR, '#dataTable td').text
                        if msg == '该条件下无数据':
                            break
                        pic_name = '%s_%s_%s_%s_p%s.png' % (channel.get('id'), game.get('name'), sd, ed, page)
                        time.sleep(2)  # 等待数据完整之后再计算整个高度
                        height = self.d.execute_script(r'''
                            var stys = window.getComputedStyle(document.body);
                            var pt = parseFloat(stys.paddingTop.replace('px', ''));
                            var pb = parseFloat(stys.paddingBottom.replace('px', ''));
                            return document.body.offsetHeight + pt + pb
                        ''')
                        cut_res = cut_img(height, self.dir_path, pic_name)
                        if not cut_res['succ']:
                            logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (
                            self.dir_path, pic_name))
                        logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
                        # time.sleep(2)
                        try:
                            WebDriverWait(self.d, 1).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '#id_page .next'))).click()
                            page += 1
                            continue
                        except:
                            break
            return {'succ': True, 'msg': 'img got success'}
        except Exception as e:
            logger.error(e, exc_info=1)
            self.d.quit()
            return {'succ': False, 'msg': e}

    def get_data(self, cookie, osd, oed):
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'cookie': cookie,
            'origin': 'https://s.qq.com',
            'referer': 'https://s.qq.com/tx/data/center.html',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }

        # 请求1
        gamelist_url = 'https://s.qq.com/service/datacenter/gamelist'
        gamelist_data = None
        gameres = post(gamelist_url, gamelist_data, headers=headers)
        if not gameres.get('is_success'):
            logger.error(gameres.get('msg'), exc_info=1)
            return {'succ': False, 'data': gameres.get('msg')}
        if gameres['msg'].status_code != 200:
            return {'succ': False, 'data': "{'msg': 'game status_code not 200'}"}
        gameres = gameres['msg'].content.decode('utf-8')
        gameres = json.loads(gameres)
        if gameres['ret'] != 0:
            return {'succ': False, 'data': "{'msg':'game data error'}"}
        # if len(gameres['result']) == 0:
        #     return {'succ': False, 'data':"{'msg':'no game data'}"}

        # 请求2
        channellist_url = 'https://s.qq.com/service/datacenter/channellist'
        channellist_data = None
        channelres = post(channellist_url, channellist_data, headers=headers)
        if not channelres.get('is_success'):
            logger.error(channelres.get('msg'), exc_info=1)
            return {'succ': False, 'data': channelres.get('msg')}
        if channelres['msg'].status_code != 200:
            return {'succ': False, 'data': "{'msg': 'channellist status_code not 200'}"}
        channelres = channelres['msg'].content.decode('utf-8')
        channelres = json.loads(channelres)
        if gameres['ret'] != 0:
            return {'succ': False, 'data': "{'msg':'channellist data error'}"}
        # if len(gameres['result']) == 0:
        #     return {'succ': False, 'data':"{'msg':'no channellist data'}"}

        # 请求3
        total = -1
        pagesize = 500
        pageno = 0
        alldetails = []
        while total == -1 or (pageno + 1) <= math.ceil(total % pagesize):  # 未请求，或者未请求完所有分页，循环请求
            details_url = 'https://s.qq.com/service/datacenter/details'
            gameidarr = []
            gamemap = {}
            for gameitem in gameres['result']:
                gameidarr.append(str(gameitem['id']))
                gamemap[gameitem['id']] = gameitem['name']
            channelidarr = []
            for channelitem in channelres['result']:
                channelidarr.append(str(channelitem['id']))
            details_data = {
                'tStartTime': osd,
                'tEndTime': oed,
                'vChannelId': json.dumps(channelidarr),
                'vGameId': json.dumps(gameidarr),
                'iPageNo': pageno,
                'iPageSize': pagesize,  # 最大支持500
                'iType': 0
            }
            logger.info('req details, pageno:%d, total:%d' % (pageno, total))
            detailsres = post(details_url, details_data, headers=headers)
            if not detailsres['is_success']:
                logger.error('%s\n%s' % (details_url, details_data))
                pageno += 1
                continue
            detailsres = detailsres['msg'].content.decode('utf-8')
            detailsres = json.loads(detailsres)
            if detailsres['ret'] != 0:
                logger.info('details_data:%s, header:%s, detailres:%s' % (details_data, headers, detailsres))
                return {'succ': False, 'data': "{'msg':'detail data error'}"}
            # if len(detailsres['result']['rows']) == 0:
            #     logger.info('details_data:%s, header:%s, detailres:%s' % (details_data, headers, detailsres))
            #     return {'succ': False, 'data':"{'msg':'no detail data'}"}
            for detailitem in detailsres['result']['rows']:
                detailitem['gameappname'] = gamemap.get(detailitem['gameappid'])
                alldetails.append(detailitem)

            total = detailsres['result']['total']
            pageno += 1

        return {'succ': True, 'data': json.dumps(alldetails, ensure_ascii=False),
                'options': {'gameList': gameres.get('result'), 'channelList': channelres.get('result')}}

    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)

        # 登陆
        login_res = self.runLogin(ui)
        # self.d.quit()
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')

        # 获取上个月到现在每天的数据
        data_list = []
        for start_date, end_date in days:
            try:
                res = self.get_data(cookies, start_date, end_date)
                file_name = os.path.join(self.dir_path, '%s_%s.json' % (start_date, end_date))
                if not res['succ']:
                    return {'succ': False, 'msg': res['data']}
                if not res.get('data'):
                    continue
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(res['data'])
                data_list.append([start_date, end_date, res.get('options')])
                time.sleep(0.25)
            except Exception as e:
                logger.error('sth error about get data function')
                logger.error(e, exc_info=1)

        for sd, ed, data in data_list:
            try:
                self.getImg(sd, ed, data)
            except Exception:
                self.save_screen_shot(self.err_img_name)
                continue

        if not data_list:
            return {'succ': True, 'msg': 'no data'}
        return {'succ': True}

