from requests.utils import quote
from re import search
from lxml.html import etree

import logging
import time

from platform_crawler.spiders.icbc.icbc_base_crawler import BaseCrawler


logger = None


class CompareBillCrawlers(BaseCrawler):
    def __init__(self, sessionid, cookie, **kwargs):
        global logger
        self.sessionid = sessionid
        self.cookie = cookie
        self.headers = kwargs.get('headers')
        self.base_url = 'https://corporbank-simp.icbc.com.cn'
        logger = logging.getLogger(kwargs.get('spider'))
        super().__init__(**kwargs)

    def crawler_and_save(self, first_date, last_date):
        """爬取对账单搜索页面"""
        url = "%s/ebankc/newnormalbank/account/e_CompareBill.jsp" % self.base_url
        params = {'dse_sessionId': self.sessionid, 'menuitemchain': '|E206|E19'}
        res = self.deal_result(self.execute('GET', url, params=params), err_type='icbc')         # 对账单页面
        if not res.get('succ'):
            return res
        return self.parse_search_page(res, first_date, last_date)

    def parse_search_page(self, res, first_date, last_date):
        """解析对账单搜索页面，构建搜索条件"""
        ys, ms, ds = first_date.split('-')
        ye, me, de = last_date.split('-')
        html = etree.HTML(res.get('msg'))
        build_pay_load = {}
        ch_date = lambda x:  x if len(x) == 2 else '0%s' % x
        for e in html.xpath('//input[@type="hidden"]'):
            name = e.xpath('./@name')[0]
            try:
                value = e.xpath('./@value')[0]
            except:
                value = ""
            value = quote(value.encode('gbk'))
            if name == 'Begin_date':
                value = ''.join([ys, ms, ch_date(ds)])
            elif name == 'End_date':
                value = ''.join([ye, me, ch_date(de)])
            elif name == 'Qry_date':
                value = ys
            build_pay_load[name] = value

        base_payload = {'Corpor_id': '1', 'Account_num': '4000010109200194412', 'yearname1': ys,
                        'dayname1': ds, 'yearname2': ye, 'monthname2': me, 'dayname2': de, 'monthname1': ms,}
        build_pay_load.update(base_payload)
        build_pay_load = '&'.join(['%s=%s' % (k, v) for k, v in build_pay_load.items()])
        search_url = '%s/servlet/com.ibm.btt.cs.servlet.CSReqServlet' % self.base_url
        # 搜索对账单
        res = self.deal_result(self.execute('POST', search_url, data=build_pay_load, content_type='application/x-www-form-urlencoded'), err_type='icbc')
        if not res.get('succ'):
            return res

        # 分页爬取数据
        data_list = []
        for p in range(20, 200, 20):
            logger.info('begin_pos:----------------------------%s' % p)
            data, html = self.crawler_down_list(res.get('msg'))
            if not data:
                continue
            data_list.extend(data)
            payload = self.build_next_payload(html, p)
            if not payload:
                time.sleep(0.25)
                continue
            res = self.deal_result(self.execute('POST', search_url, data=payload, content_type='application/x-www-form-urlencoded'))
            if res.get('succ'):
                time.sleep(0.25)
                continue
            time.sleep(0.25)
        else:
            return {'succ': True, 'data': data_list}

    def xpath(self, element, xpath):
        res = element.xpath(xpath)
        return res[0] if len(res) > 0 else ''

    def crawler_down_list(self, html_content):
        """解析页面数据"""
        html_content = etree.HTML(html_content)
        items = html_content.xpath('//table[@align="center"]//tr')[1:]
        data = []
        for i in items:
            item = {}
            item['date'] = self.xpath(i, './td[1]/text()')             # 日期
            item['cb_tran_type'] = self.xpath(i, './td[2]/text()')     # 交易类型   1
            item['cert_type'] = self.xpath(i, './td[3]/text()')        # 凭证种类
            item['cert_num'] = self.xpath(i, './td[4]/text()')         # 凭证号
            item['dest_account'] = self.xpath(i, './td[5]/text()')     # 对方账号
            item['dest_name'] = self.xpath(i, './td[6]/text()')        # 对方户名
            item['summary'] = self.xpath(i, './td[7]/text()')          # 摘要     1
            item['lend_money_num'] = self.xpath(i, './td[8]/text()')   # 借方发生额(支出)
            item['income_num'] = self.xpath(i, './td[9]/text()')       # 贷方发生额
            item['balance'] = self.xpath(i, './td[10]/text()')         # 余额
            data.append(item)
            logger.info(item)
        return data, html_content

    def build_next_payload(self, html, page_num):
        """构造下一页搜索条件"""
        payload = {}
        inp = html.xpath('//input[@type="hidden"]')
        encode_list = ['MenuChain', 'Transaction_name', 'serialnodsrUP']
        for i in inp:
            name = i.xpath('./@name')[0]
            try:
                value = i.xpath('./@value')[0]
            except:
                value = ''
            if name == 'Begin_pos':
                value = str(page_num)
            if name in encode_list:
                value = quote(value.encode('gbk'))
            payload[name] = value
        payload = '&'.join(['%s=%s' % (k, v) for k, v in payload.items()])
        return payload
