from requests.utils import quote
from re import search
from lxml.html import etree

import logging
import time

from platform_crawler.spiders.icbc.icbc_base_crawler import BaseCrawler


logger = None


class EbillCrawlers(BaseCrawler):
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
        url = "%s/ebankc/newnormalbank/account/queryEbill.jsp" % self.base_url
        params = {'dse_sessionId': self.sessionid, 'menuitemchain': '|E205|E19'}
        res = self.deal_result(self.execute('GET', url, params=params), err_type='icbc')         # 回单搜索页面
        if not res.get('succ'):
            return res
        parse_res = self.parse_search_page(res, first_date, last_date)
        if not parse_res.get('succ'):
            return parse_res
        return self.parse_detail(parse_res.get('data'))

    def parse_search_page(self, res, first_date, last_date):
        """解析对账单搜索页面，构建搜索条件"""
        ys, ms, ds = first_date.split('-')
        ye, me, de = last_date.split('-')
        html = etree.HTML(res.get('msg'))
        build_pay_load = {}
        ch_date = lambda x:  x if len(x) == 2 else '0%s' % x
        # turn_list = ['MenuChain', 'Transaction_name']
        for e in html.xpath('//input[@type="hidden"]'):
            name = e.xpath('./@name')[0]
            try:
                value = e.xpath('./@value')[0]
            except:
                value = ""
            # if name in turn_list:
            value = quote(value.encode('gbk'))
            if name == 'Begin_date':
                value = ''.join([ys, ms, ch_date(ds)])
            elif name == 'End_date':
                value = ''.join([ye, me, ch_date(de)])
            build_pay_load[name] = value

        base_payload = {'Corpor_id': '1', 'Account_num': '4000010109200194412', 'yearname1': ys,
                        'dayname1': ds, 'yearname2': ye, 'monthname2': me, 'dayname2': de, 'monthname1': ms,}
        build_pay_load.update(base_payload)
        build_pay_load = '&'.join(['%s=%s' % (k, v) for k, v in build_pay_load.items()])
        search_url = '%s/servlet/com.ibm.btt.cs.servlet.CSReqServlet' % self.base_url
        res = self.deal_result(self.execute('POST', search_url, data=build_pay_load, content_type='application/x-www-form-urlencoded'), err_type='icbc')       # 搜索回单
        if not res.get('succ'):
            return res

        # 分页爬取数据
        data_list = []
        for p in range(20, 300, 20):
            logger.info('begin_pos: -------------------------- %s' % p)
            data, html = self.crawler_down_list(res.get('msg'))
            if not data:
                continue
            data_list.extend(data)
            payload = self.build_next_payload(html, p, base_payload)
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
        return res[0].strip() if len(res) > 0 else ''

    def crawler_down_list(self, html_content):
        """解析页面数据"""
        html_content = etree.HTML(html_content)
        items = html_content.xpath('//table[@class="mainarea"]/tr[4]/td/table/tr')[1:]
        data = []
        # turn_list = ['Transaction_name', 'Corpor_name_c', 'Rec_Account_name', 'Trans_abstr', 'Trans_type', 'PostScript']
        ret_payload = {'inner_url': '%s%s' % (self.base_url, '/servlet/com.ibm.btt.cs.servlet.CSReqServlet')}
        for p in html_content.xpath('//form[@name="thisform"]/input'):
            name = self.xpath(p, './@name')
            value = self.xpath(p, './@value')
            ret_payload[name] = quote(value.encode('gbk'))
        for i in items:
            item = {}
            item['serial_num'] = self.xpath(i, './td[2]/div/text()')                    # 回单序列号
            item['our_account'] = self.xpath(i, './td[3]/div/text()')                   # 本方账号
            item['our_account_name'] = self.xpath(i, './td[4]/div/text()')              # 本方户名
            item['rec_account'] = self.xpath(i, './td[5]/div/text()')                   # 对方账号
            item['rec_account_name'] = self.xpath(i, './td[6]/div/text()')              # 入账日期
            item['date_of_application'] = self.xpath(i, './td[7]/div/text()')           # 回单申请日期
            item['time_of_application'] = self.xpath(i, './td[8]/div/text()')           # 回单申请时间
            ret_payload['Ebill_Serialno'] = item.get('serial_num')
            item['serial_params'] = ret_payload
            data.append(item)
            logger.info(item)
        return data, html_content

    def build_next_payload(self, html, page_num, base_payload):
        """构造下一页搜索条件"""
        payload = {}
        inp = html.xpath('//form[@name="thisform1"]//input[@type="hidden"]')
        # encode_list = ['MenuChain', 'Transaction_name', 'serialnodsrUP', 'Rec_Account_name', 'Trans_abstr']
        for i in inp:
            try:
                name = i.xpath('./@name')[0]
            except:
                continue
            try:
                value = i.xpath('./@value')[0]
            except:
                value = ''
            if name == 'Begin_pos':
                value = str(page_num)
            # if name in encode_list:
            value = quote(value.encode('gbk'))
            payload[name] = value
        payload.update(base_payload)
        payload = '&'.join(['%s=%s' % (k, v) for k, v in payload.items()])
        return payload

    def parse_detail(self, data_list):
        """爬取历史详细信息"""
        # referer = 'https://corporbank-simp.icbc.com.cn/servlet/com.ibm.btt.cs.servlet.CSReqServlet'
        for i in data_list:
            url = i.get('serial_params').get('inner_url')
            pl_dict = i.get('serial_params')
            try:
                pl_dict['Ebill_Serialno'] = i.get('serial_num')
            except:
                pass
            payload = '&'.join(['%s=%s' % (k, v) for k, v in pl_dict.items() if k != 'inner_url'])
            detail_page = self.deal_result(self.execute('POST', url, data=payload, content_type='application/x-www-form-urlencoded'), err_type='icbc')
            if not detail_page.get('succ'):
                time.sleep(0.25)
                continue
            detail_data = self.parse_detail_content(detail_page.get('msg'))
            i['detail_content'] = detail_data
            logger.info(detail_data)
        return {'succ': True, 'data': data_list}

    def parse_detail_content(self, page):
        """解析点击回单按钮弹出的页面"""
        detail = []
        html = etree.HTML(page)
        for tr in html.xpath('//table[@class="detailArea commonTable"]//tr'):
            name = self.xpath(tr, './td[1]/text()')
            value = self.xpath(tr, './td[2]/text()')
            # if value:
            #     value = value.encode('gbk').decode('utf-8', 'ignore')
            detail.append({'name': name, 'value': value})
        return detail

