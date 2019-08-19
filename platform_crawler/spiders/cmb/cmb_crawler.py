from lxml.html import etree
from re import search
import time
import json
import os
import requests

from platform_crawler.spiders.cmb.cmb_base_crawler import BaseCrawler
from platform_crawler.utils.utils import Util


logger = None


class CmbCrawler(BaseCrawler):

    def __init__(self, session_id=None, list_url=None, **kwargs):
        self.list_url = list_url
        self.session_id = session_id
        self.headers = kwargs.get('headers')
        self.base_url = 'https://ubank.cmbchina.com'
        super().__init__(**kwargs)

    def crawl_page_list(self):
        year, this_month, today = time.strftime('%Y-%m-%d').split('-')
        if int(today) < 25:
            day_len = Util().mDays(int(year), int(this_month)-1)
            day = str(day_len-25+int(today))
        else:
            day = str(int(today)-25)
        month = str(int(this_month)-1) if int(today) < 25 else this_month
        z = lambda x: x if len(str(x)) == 2 else '0%s' % x
        first_date = '%s%s%s' % (year, z(month), z(day))
        last_date = '%s%s%s' % (year, z(this_month), z(today))
        data = self.crawl(first_date, last_date)
        if isinstance(data, list):
            self.save(data)
            return True
        else:
            return False

    def deal_result(self, result, json_str=False, err_type=None):
        self.base_result(json_str=json_str)
        if not self.ret.get('succ'):
            return False
        if self.ret.get('succ'):
            # 处理链接失效
            reg = r'为了您的帐户安全，请使用移动客户端访问企业手机银行'
            try:
                data = search(reg, self.ret.get('msg')).group()
            except:
                data = ''
            if data == '为了您的帐户安全，请使用移动客户端访问企业手机银行':
                logger.warning('login lost')
                return False
            return True

    def crawl(self, first_date, last_date):
        payload = 'startDate=%s&endDate=%s' % (first_date, last_date)
        if not self.deal_result(self.execute('POST', self.list_url, data=payload, content_type='application/x-www-form-urlencoded'), err_type='cmb'):
            return False
        self.ret['msg'] = self.ret.get('msg').replace('<?xml version="1.0" encoding="UTF-8"?>', '')
        html = etree.HTML(self.ret.get('msg'))
        data_list = self.parse(html)
        if not isinstance(data_list, list):
            return data_list
        pages = html.xpath('//input[@id="pageCounts"]/@value')[0]
        next_page_url = self.xpath(html, '//form[@id="pageform"]/@action')
        next_url = '%s%s' % (self.base_url, next_page_url)
        if int(pages) > 1:
            for p in range(2, int(pages) + 1):
                payload = 'pageHandler.page=%s' % p
                if not self.deal_result(self.execute('POST', next_url, data=payload), err_type='cmb'):
                    return False
                self.ret['msg'] = self.ret.get('msg').replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                html = etree.HTML(self.ret.get('msg'))
                parse_res = self.parse(html)
                if not isinstance(parse_res, list):
                    return parse_res
                data_list.extend(parse_res)

        return self.crawl_detail(data_list)

    def xpath(self, element, text):
        ele = element.xpath(text)
        return ele[0] if isinstance(ele, list) and len(ele) > 0 else ''

    def parse(self, html):
        tables = html.xpath('//div[@class="fbm_list"]/div')[1:]
        data_list = []
        for div in tables:
            data = {}
            for tr in div.xpath('.//tr'):
                if self.xpath(tr, './th/text()') == '交易日:':
                    tran_date = self.xpath(tr, './td/text()')
                    tran_date = '%s-%s-%s 00:00:00' % (tran_date[:4], tran_date[4:6], tran_date[6:])
                    data['tranDate'] = tran_date
                elif self.xpath(tr, './th/text()') == '借:':
                    bf_type = self.xpath(tr, './td/text()')
                    data['debitAmount'] = bf_type.replace(',', '') if bf_type else ''
                elif self.xpath(tr, './th/text()') == '贷:':
                    bf_type = self.xpath(tr, './td/text()')
                    data['creditAmount'] = bf_type.replace(',', '') if bf_type else ''
                elif self.xpath(tr, './th/text()') == '余额:':
                    data['balance'] = self.xpath(tr, './td/text()').replace(',', '')
                elif self.xpath(tr, './th/text()') == '摘要:':
                    data['summary'] = self.xpath(tr, './td/text()')
                elif self.xpath(tr, './th/text()') == '收(付)方名称:':
                    data['partyCompanyName'] = self.xpath(tr, './td/text()')
                elif self.xpath(tr, './th/text()') == '收(付)方账号:':
                    data['partyAccount'] = self.xpath(tr, './td/text()')
                elif self.xpath(tr, './th/text()') == '交易类型:':
                    data['tranType'] = self.xpath(tr, './td/text()')
            data['bankflowType'] = 2 if data.get('debitAmount') else 1
            data['detail_url'] = '%s%s' % (self.base_url, self.xpath(div, './/a/@href'))
            data_list.append(data)
        return data_list

    def crawl_detail(self, data_list):
        for d in data_list:
            url = d.pop('detail_url')
            if not self.deal_result(self.execute('GET', url, referer=self.list_url), err_type='cmb'):
                return False
            self.ret['msg'] = self.ret.get('msg').replace('<?xml version="1.0" encoding="UTF-8"?>', '')
            html = etree.HTML(self.ret.get('msg'))
            d.update(self.parse_detail(html, d))
            logger.info(d)
            time.sleep(0.2)
        return data_list

    def parse_detail(self, html, data):
        for tr in html.xpath('//tr'):
            if self.xpath(tr, './th/text()') == '账户:':
                td = self.xpath(tr, './td/text()')
                place, account, mt, our_company_name = td.split(',')
                data.update({'ourAccount': account, 'ourCompanyName': our_company_name})
            elif self.xpath(tr, './th/text()') == '起息日:':
                data['interestDate'] = self.xpath(tr, './td/text()')
            elif self.xpath(tr, './th/text()') == '流水号:':
                data['tranNo'] = self.xpath(tr, './td/text()')
            elif self.xpath(tr, './th/text()') == '收(付)方开户行:':
                data['partyBankName'] = self.xpath(tr, './td/text()')
            elif self.xpath(tr, './th/text()') == '收(付)方开户地:':
                data['partyBankAddress'] = self.xpath(tr, './td/text()')
            elif self.xpath(tr, './th/text()') == '业务参考号:':
                data['busRefNo'] = self.xpath(tr, './td/text()')
        if data.get('busRefNo'):
            data['tranTime'] = data.get('busRefNo')[-6:]
        create_time = time.strftime('%Y-%m-%d %H:%M:%S')
        data.update({'createTime': create_time, 'updateTime': create_time})
        return data

    def save(self, data):
        url = "http://erp.btomorrow.cn/adminjson/ERP_AddBankFlow"
        for dat in data:
            pay_or_get = 'creditAmount' if dat.get('creditAmount') else 'debitAmount'
            tran_time = dat.get('tranTime') if dat.get('tranTime') else ''
            sql = "INSERT INTO `t_bank_flow`(`createTime`, `updateTime`, `bankflowType`, `tranDate`, `tranTime`, " \
                  "`interestDate`, `tranType`, `%s`, `ourAccount`, `ourCompanyName`, `balance`, `summary`, " \
                  "`tranNo`, `busRefNo`, `partyCompanyName`, `partyAccount`, `partyBankName`, `partyBankAddress`, `visable`)  " \
                  "SELECT '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','1' " \
                  "from DUAL where not exists (select tranNo from t_bank_flow where tranNo='%s');" % (
                      pay_or_get, dat.get('createTime'), dat.get('updateTime'), dat.get('bankflowType'), dat.get('tranDate'),
                      tran_time, dat.get('interestDate'), dat.get('tranType'), dat.get(pay_or_get), dat.get('ourAccount'),
                      dat.get('ourCompanyName'), dat.get('balance'), dat.get('summary'), dat.get('tranNo'), dat.get('busRefNo'),
                      dat.get('partyCompanyName'), dat.get('partyAccount'), dat.get('partyBankName'), dat.get('partyBankAddress'),
                      dat.get('tranNo'))
            pay_load = {"opType": 1, "token": "dsjuei4mdnjklk2ldhjdldlanmdsajdhsajh", "sql": sql}
            self.headers = {'Content-Type': 'application/json'}
            res = self.execute('POST', url, data=json.dumps(pay_load), print_payload=False)
            if not res.get('succ'):
                logger.error(res.get('msg'))
            logger.info(sql)
            logger.info(res.get('msg').text)


def post_data(statusinfo='9999-login lost'):
    # post data and status
    data = {'type': 1, 'cmbcookie': '', 'cmblistUrl': '', 'username': '10086111'}
    json_data = {
        'json_str': data,
        'result_status': '9999-login lost'
    }
    session = requests.session()
    url = 'http://erp.btomorrow.cn/adminjson/ERP_SaveCrawlerStatus'
    try:
        resp = session.post(url, data=json.dumps(json_data), timeout=10).json()
        logger.info(resp)
        if resp['errorCode'] != 0:
            logger.info('结果上报失败: %s\n%s' % (json.dumps(data), statusinfo))
        logger.info('上报成功： %s' % (json_data))
    except Exception as es:
        logger.error(es, exc_info=1)
    finally:
        session.close()


def cmb_run(sid=None, list_url=None, spider=None):
    global logger
    sid = "JSESSIONID=00008W4youy7X-Ms0bvZ9QEaQaQ:1883m3ce3" if not sid else sid
    list_url = list_url if list_url else 'https://ubank.cmbchina.com/html/--QmJXWHFLeTQ3M0w0Zm9Ddlo-Q1oycS49aSZxWG4zcT1P.--'
    log_path = os.path.abspath('.')
    spider = 'cmb_crawler' if not spider else spider
    logger = Util().record_log(log_path, spider)
    headers = {
        'Host': "ubank.cmbchina.com",
        'Origin': "https://ubank.cmbchina.com",
        'Content-Type': "application/x-www-form-urlencoded",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'Referer': "https://ubank.cmbchina.com/html/accmgr/inputDate.jsp",
        'Cookie': sid,
    }
    cc = CmbCrawler(session_id=sid, list_url=list_url, headers=headers, spider=spider)
    cc.crawl_page_list()
    post_data()


if __name__ == '__main__':
    cmb_run()

