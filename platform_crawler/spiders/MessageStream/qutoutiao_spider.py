from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.get_login_data.login_qutoutiao import QuTouTiao


from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os


u = Util()
logger = None


class QuTouTiaoSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(user_info=user_info, **kwargs)
        self.cookie_list = None
        self.cookie_str = None
        logger = self.logger

    def set_date(self, sd, ed):
        """更新起止日期"""
        self.wait_element(By.ID, 'ctrlmcaldailyTotalDateRegion', ec=EC.element_to_be_clickable).click()
        ys, ms, ds = sd.split('-')
        ye, me, de = ed.split('-')
        setDateJs = """
ys=document.querySelector('#ctrlselectctrlmcaldailyTotalDateRegionbeginyearitem%(year_start)s');
esui.util.get('ctrlmcaldailyTotalDateRegionbeginyear')._itemClickHandler(ys);
ms=document.querySelector('#ctrlselectctrlmcaldailyTotalDateRegionbeginmonthitem%(mth_start)s');
esui.util.get('ctrlmcaldailyTotalDateRegionbeginmonth')._itemClickHandler(ms);
ye=document.querySelector('#ctrlselectctrlmcaldailyTotalDateRegionendyearitem%(year_end)s');
esui.util.get('ctrlmcaldailyTotalDateRegionendyear')._itemClickHandler(ye);
me=document.querySelector('#ctrlselectctrlmcaldailyTotalDateRegionendmonthitem%(mth_end)s');
esui.util.get('ctrlmcaldailyTotalDateRegionendmonth')._itemClickHandler(me);
ds=document.querySelector('#ctrlmonthctrlmcaldailyTotalDateRegionbeginmonthview%(year_start_of_day)s-%(mth_start)s-%(day_start)s');
esui.util.get('ctrlmcaldailyTotalDateRegionbeginmonthview')._selectByItem(ds);
de=document.querySelector('#ctrlmonthctrlmcaldailyTotalDateRegionendmonthview%(year_end_of_day)s-%(mth_end)s-%(day_end)s');
esui.util.get('ctrlmcaldailyTotalDateRegionendmonthview')._selectByItem(de);
"""
        setDateJs = setDateJs % {'year_start': int(ys[-2:])-1, 'mth_start': int(ms)-1, 'year_end': int(ye[-2:])-1,
                                 'mth_end': int(me)-1, 'day_start': int(ds), 'day_end': int(de), 'year_start_of_day': ys,
                                 'year_end_of_day': ye}
        logger.info(setDateJs)
        self.d.execute_script(setDateJs)
        self.wait.until(EC.element_to_be_clickable((By.ID, 'ctrlbuttonctrlmcaldailyTotalDateRegionok'))).click()

    def get_img(self):
        """截图，并处理图片文件"""
        self.d.get('http://adv.aiclk.com/#/report/index')
        self.d.implicitly_wait(3)
        time.sleep(1)
        try:
            dates = self.get_dates
            for sd, ed in dates:
                try:
                    self.d.find_element_by_id('close_notice_box').click()
                except:
                    pass
                self.set_date(sd, ed)          # 更新日期
                # 等待数据表
                self.wait_element(By.ID, 'ctrltabledailyTotalList')
                # 截图
                pic_name = '%s_%s.png' % (sd, ed)
                cut_res = cut_img(None, self.dir_path, pic_name)
                if not cut_res['succ']:
                    logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
                logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
                time.sleep(2)
            else:
                return {'succ': True, 'msg': 'img got success'}
        except Exception as e:
            logger.error(e, exc_info=1)
            self.save_screen_shot(self.err_img_name)
            return {'succ': False, 'msg': e}
        finally:
            self.d.quit()

    def get_data(self, osd, oed):
        sd = '%s%s%s' % tuple(osd.split('-'))
        ed = '%s%s%s' % tuple(oed.split('-'))
        url = "http://adv.aiclk.com/report/bill/%s-%s?_=%s" % (sd, ed, round(time.time()*1000))
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "cookie": self.cookie_str,
            "host": "adv.aiclk.com",
            "Referer": 'http://adv.aiclk.com/',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        }
        data = self.deal_result(self.execute('GET', url, headers=headers), json_str=True)
        if not data['succ']:
            raise Exception(data.get('msg'))
        file_name = os.path.join(self.dir_path, '%s_%s.json' % (osd, oed))
        data = data.get('msg')
        if not data:
            return {'succ': True, 'msg': 'no data'}
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        logger.info('crawled data: %s' % data)
        return {'succ': True}

    def get_balance(self):
        url = 'http://adv.aiclk.com/users/info'
        ref = 'http://adv.aiclk.com/new/index.html'
        res = self.deal_result(self.execute('GET', url, referer=ref), json_str=True)
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        data = res.get('msg').get('data')
        balance = (data.get('balance') + data.get('coupon'))/100
        self.balance_data = [{'账号': self.acc, '余额': balance}]

    def parse_balance(self):
        header = ['账号', '余额']
        return header, self.balance_data

    def login_part(self, ui):
        self.login_obj = QuTouTiao(ui, '%s.login' % ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res['succ']:
            return login_res
        elif login_res.get('succ') and login_res.get('msg') == '开户资料正在审核中':
            return {'succ': True}
        # 获取登录后浏览器驱动和数据
        self.d = login_res.pop('driver')
        self.wait = WebDriverWait(self.d, 20)
        self.cookie_list = login_res.get('cookies')
        self.cookie_str = '; '.join(f'{e.get("name")}={e.get("value")}' for e in self.cookie_list)

    def get_img_part(self, *args, **kwargs):
        # 截图操作
        img_res = self.get_img()
        if not img_res.get('succ'):
            return img_res

    def get_data_part(self, ui, **kwargs):
        days = self.get_dates
        # 获取上个月到现在每天的数据
        err_list, data_list = [], []
        for start_date, end_date in days:
            res = self.get_data(start_date, end_date)
            if res['succ'] and res.get('msg') == 'no data':
                time.sleep(0.25)
                continue
            elif not res.get('succ'):
                return {'succ': False, 'msg': err_list}
            data_list.append(1)
        if not data_list:
            self.result_kwargs['has_data'] = 0
        return {'succ': True}
