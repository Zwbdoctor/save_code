import time
import json
import os

from platform_crawler.spiders.cmb.cmb_base_crawler import BaseCrawler
from platform_crawler.utils.utils import Util

logger = None


class EbankCrawler(BaseCrawler):

    def __init__(self, cookie=None, list_url=None, **kwargs):
        self.list_url = list_url
        self.cookie = cookie
        self.headers = kwargs.get('headers')
        self.base_url = 'https://ebank.95559.com.cn'
        super().__init__(**kwargs)

    def crawl_page_list(self):
        year, this_month, today = time.strftime('%Y-%m-%d').split('-')
        if int(today) < 25:
            day_len = Util().mDays(int(year), int(this_month) - 1)
            day = str(day_len - 25 + int(today))
        else:
            day = str(int(today) - 25)
        start_month = str(int(this_month) - 1) if int(today) < 25 else this_month
        z = lambda x: x if len(str(x)) == 2 else '0%s' % x
        first_date = '%s%s%s' % (year, z(start_month), z(day))
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
            if self.ret.get('msg').get('RSP_HEAD').get('ERROR_MESSAGE') == '会话异常，请重新登陆':
                logger.warning('login lost')
                return False
            return True

    def crawl(self, first_date, last_date):
        url = "https://ebank.95559.com.cn/CEBS/aq/cb0104_accDetailTradeDetailQry.ajax"
        payload = {"REQ_MESSAGE": json.dumps({
            "REQ_HEAD": {}, "REQ_BODY": {"step": "_ql", "accNo": "655655102018800110122", "accName": "霍尔果斯光速网络科技有限公司",
                                         "beginDate": first_date, "endDate": last_date,
                                         "minAmt": "", "maxAmt": "", "qryType": "1",
                                         "CCY": "CNY", "beginNo": "0", "firstFlg": "Y", "type": "3", "pageFlag": "3",
                                         "doFlag": "1", "npldBal": "",
                                         "inqBegIndRec": "", "bizNo": "", "endFlag": "", "queryFieldType": "1",
                                         "cloudFlag": "0", "queryDetailType": "1",
                                         "downAcc": "",
                                         "pageNo": "1", "pageSize": "20"}})}
        if not self.deal_result(self.execute('POST', url, data=payload), err_type='cmb', json_str=True):
            return False
        data = self.ret.get('msg').get('RSP_BODY').get('rows')
        return self.parse(data)

    def xpath(self, element, text):
        ele = element.xpath(text)
        return ele[0] if isinstance(ele, list) and len(ele) > 0 else ''

    def parse(self, json_data):
        data_list = []
        key_list = ['tranTime', 'dcStr', 'amount', 'balance', 'abstractInf', 'vchNo', 'oppAccName', 'oppAccNo']
        for j in json_data:
            data = {k: v for k, v in j.items() if k in key_list}
            data['tranDate'] = '%s 00:00:00' % data.get('tranTime').split(' ')[0]
            data['tranTime'] = data.get('tranTime').split(' ')[1].replace(':', '')
            data['tranType'] = data.pop('abstractInf')
            data['bankflowType'] = 2 if data.pop('dcStr') == '借' else 1
            amount_key = 'debitAmount' if data.get('bankflowType') == 2 else 'creditAmount'
            data[amount_key] = data.pop('amount')
            data['ourAccount'] = '655655102018800110122'
            data['ourCompanyName'] = '霍尔果斯光速网络科技有限公司'
            data['summary'] = data.get('tranType')
            tran_date = data.get('tranDate').split(' ')[0].replace('-', '').replace(' ', '').replace(':', '')
            data['tranNo'] = 'hrgs%s%s%s' % (tran_date, data.get('tranTime'), float(data.get(amount_key)))
            data['partyCompanyName'] = data.pop('oppAccName')
            data['partyAccount'] = data.pop('oppAccNo')
            create_time = time.strftime('%Y-%m-%d %H:%M:%S')
            data['createTime'] = create_time
            data['updateTime'] = create_time
            data_list.append(data)
        return data_list

    def save(self, data):
        url = "http://erp.btomorrow.cn/adminjson/ERP_AddBankFlow"
        for dat in data:
            pay_or_get = 'creditAmount' if dat.get('creditAmount') else 'debitAmount'
            sql = "INSERT INTO `t_bank_flow`(`createTime`, `updateTime`, `bankflowType`, `tranDate`, `tranTime`, " \
                  "`tranType`, `%s`, `ourAccount`, `ourCompanyName`, `balance`, `summary`, " \
                  "`tranNo`, `partyCompanyName`, `partyAccount`, `visable`)  " \
                  "SELECT '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'" \
                  "from DUAL where not exists (select tranNo from t_bank_flow where tranNo='%s');" % (
                      pay_or_get, dat.get('createTime'), dat.get('updateTime'), dat.get('bankflowType'),
                      dat.get('tranDate'), dat.get('tranTime'), dat.get('tranType'), dat.get(pay_or_get),
                      dat.get('ourAccount'), dat.get('ourCompanyName'), dat.get('balance'), dat.get('summary'),
                      dat.get('tranNo'), dat.get('partyCompanyName'), dat.get('partyAccount'), 1, dat.get('tranNo'))
            pay_load = {"opType": 1, "token": "dsjuei4mdnjklk2ldhjdldlanmdsajdhsajh", "sql": sql}
            self.headers = {'Content-Type': 'application/json'}
            res = self.execute('POST', url, data=json.dumps(pay_load), print_payload=False)
            if not res.get('succ'):
                logger.error(res.get('msg'))
            logger.info(sql)
            logger.info(res.get('msg').text)


def ebank_run(cookie=None, spider=None):
    global logger
    cookie = "com.bocom.cebs.base.resolver.CEBSSmartLocaleResolver.LOCALE=zh_CN; JSESSIONID=0000aDGgxUDXj-141Az5eHtwaGc:-1" if not cookie else cookie
    log_path = os.path.abspath('.')
    spider = 'ebank_crawler' if not spider else spider
    logger = Util().record_log(log_path, spider)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        'Host': "ebank.95559.com.cn",
        'Cookie': cookie
    }
    cc = EbankCrawler(cookie=cookie, headers=headers, spider=spider)
    return cc.crawl_page_list()


if __name__ == '__main__':
    ebank_run()
