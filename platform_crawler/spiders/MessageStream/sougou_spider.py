from selenium.webdriver.common.by import By
import time
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.get_login_data.login_sougou import SouGou

u = Util()
logger = None


class SouGouSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.dates = None
        super().__init__(user_info=user_info, **kwargs)
        self.html = None
        logger = self.logger

    def get_data(self, sd, ed, page):
        """
        获取数据
        :param page: page data
        :return:
        """
        # 处理文件名
        fname = '%(sd)s_%(ed)s.json' % {'sd': sd, 'ed': ed}
        file_name = os.path.join(self.dir_path, fname)
        from lxml.html import etree
        # 处理数据
        self.html = etree.HTML(page)
        table_trs = self.html.xpath('//tbody/tr')
        if len(table_trs) == 1 and table_trs[0].xpath('./td/text()')[0].strip() == '没有记录':
            return {'succ': False, 'msg': 'no data'}
        data = {'total_count': len(table_trs), 'datas': []}
        for tr in table_trs:
            date = tr.xpath('./td[1]/text()')[0].strip()
            impression = tr.xpath('./td[2]/text()')[0].strip()
            click_times = tr.xpath('./td[3]/text()')[0].strip()
            click_rates = tr.xpath('./td[4]/text()')[0].strip()
            cost_average = tr.xpath('./td[5]/text()')[0].strip()
            cost_tatal = tr.xpath('./td[6]/text()')[0].strip()
            tr_data = {'date': date, 'impression': impression, 'click_times': click_times, 'click_rates': click_rates,
                       'cost_average': cost_average, 'cost_tatal': cost_tatal}
            data.get('datas').append(tr_data)

        # 写入文件
        with open(file_name, 'w', encoding='utf-8') as f:
            try:
                json.dump(data, f)
            except Exception as e:
                logger.error(e, exc_info=1)
        logger.info('crawled data: --------' + json.dumps(data))
        return {'succ': True}

    def parse_balance(self, *args, **kwargs):
        balance = self.html.xpath('//span[@class="red bold"]/text()')
        if not balance:
            raise Exception('Not get balance data: Something wrong with balance xpath)')
        balance = float(balance[0].strip())
        header = ['账号', '余额']
        # return header, [{'账号': self.acc, '余额': balance}]
        return header, balance

    def get_data_process(self):
        self.wait_element(By.CSS_SELECTOR, 'a.tip.fr').click()      # 进入广告投放中心
        # 获取时间
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ms=ms, ys=ys, ye=ye, me=me)
        img_data, has_data = [], []
        for sd, ed in dates:
            url = 'http://agent.e.sogou.com/main.html?pageSize=50&status=1&start=%s&end=%s' % (sd, ed)
            self.d.get(url)
            self.d.refresh()
            self.wait_element(By.XPATH, '//table')
            html = self.d.page_source           # get page data
            res = self.get_data(sd, ed, html)   # 处理数据
            if res['succ']:
                img_data.append({'hasData': True, 'sd': sd, 'ed': ed, 'img': False})
                has_data.append(1)
            elif not res['succ'] and res['msg'] == 'no data':
                img_data.append({'hasData': False, 'img': False})
                logger.warning({'hasData': False, 'img': False})
            time.sleep(0.25)
        if not has_data:
            self.result_kwargs['has_data'] = 0
        return img_data

    def update_date_use_js(self, sd, ed):
        date_js = """
document.querySelector('input.setTime.start').value="%s";
document.querySelector('input.setTime.end').value="%s";
"""
        self.d.execute_script(date_js % (sd, ed))
        self.wait_element(By.CSS_SELECTOR, 'a.search.btnA.fr').click()  # 点击查询

    def get_img(self, sd, ed):
        """截图操作"""
        # 更新日期
        self.update_date_use_js(sd, ed)
        # 选择总消耗
        select_spend = """document.querySelector('div.selectDiv.noInit .hide.cl li[data-id="1"]').click()"""
        self.d.execute_script(select_spend)
        time.sleep(2)

        # 显示产品图标
        pname = self.d.find_element_by_css_selector('span.icon.fr')
        pname_location = [pname.location.get('x'), pname.location.get('y')]
        u.pag.moveTo(x=pname_location[0], y=pname_location[1]+110)

        # 截图
        hjs = 'return h = document.body.offsetHeight'
        height = self.d.execute_script(hjs)
        pic_name = '%(sd)s_%(ed)s.png' % {'sd': sd, 'ed': ed}
        cut_res = cut_img(None, self.dir_path, pic_name)
        if not cut_res['succ']:
            logger.error('get img %s failed-------msg: %s' % (pic_name, cut_res.get('msg')))
        logger.info('height: %s ---picname: %s' % (height, pic_name))
        return cut_res

    def login_part(self, ui):
        self.login_obj = SouGou(ui, ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            return login_res
        self.d = login_res.get('driver')

    def get_data_part(self, ui):
        # 获取数据
        img_data = self.get_data_process()
        return img_data

    def get_img_part(self, get_data_res=None, **kwargs):
        # 截图部分
        for i in get_data_res:
            if i.get('hasData'):
                try:
                    res = self.get_img(i.get('sd'), i.get('ed'))
                    if not res['succ']:
                        i['img'] = True
                        logger.error(res['msg'])
                except Exception as e:
                    logger.error(e, exc_info=1)
        else:
            self.d.quit()

        return {'succ': True}
