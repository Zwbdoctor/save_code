import time
import json
import os
import logging

from platform_crawler.spiders.ccbn.ccbn_base_crawler import BaseCrawler
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.ccbn.login_ccbn import get_task_parm


logger = None


class CmbCrawler(BaseCrawler):

    def __init__(self, bsn_code=None, **kwargs):
        self.bsn_code = bsn_code
        self.headers = kwargs.get('headers')
        self.base_url = 'https://ubank.cmbchina.com'
        super().__init__(**kwargs)

    def crawl_page_list(self):
        year, this_month, today = time.strftime('%Y-%m-%d').split('-')
        month = str(int(this_month)-1) if int(today) < 25 else this_month
        if month == '0':
            month = '12'
        if int(today) < 25:
            day_len = Util().mDays(int(year), int(month))
            day = str(day_len-25+int(today))
        else:
            day = str(int(today)-25) if today != '25' else str(int(today)-24)
        syear = str(int(year) - 1) if month == '12' and month != this_month else year
        z = lambda x: x if len(str(x)) == 2 else '0%s' % x
        first_date = '%s%s%s' % (syear, z(month), z(day))
        last_date = '%s%s%s' % (year, z(this_month), z(today))
        data = self.crawl(first_date, last_date)
        if isinstance(data, list):
            self.save(data)
            return True
        else:
            return False

    def deal_result(self, result, json_str=True, err_type=None):
        self.base_result(json_str=json_str)
        if not self.ret.get('succ'):
            return False
        if self.ret.get('succ'):
            # 处理链接失效
            msg = self.ret.get('msg').get('retMsg')
            if msg == '该请求需要用户先登录' or msg == '业务流程权限校验失败':
                logger.warning('login lost')
                return False
            return True

    def crawl(self, first_date, last_date):
        url = 'https://corp.bank.ecitic.com/cotb/COTBServlet'
        # cookie = self.headers.get('Cookie')
        # bsn_code = '00010201'
        # first_date = '20190122'
        # last_date = '20190122'
        payload = {
            "txCode": 'C0102011', "accNo": '8110801013201545710', "startDate": first_date, "endDate": last_date, "maxAmt": "9999999999999.99",
            "minAmt": "0.00", "seqFlag": "A", "startNo": 1, "rcdNum": 10, "commonDataList": [
                {"bsnCode": '00010201', "clientIp": "", "language": "CN", "mac": "", "productCode": "", "random": "",
                 "sysCode": "COTB", "timeStamp": ""}]
        }
        # payload = '&'.join(['%s=%s' % (k, v) for k, v in payload.items()])
        ref = 'https://corp.bank.ecitic.com/cotb/index.html'
        if not self.deal_result(self.execute('POST', url, data=json.dumps(payload), content_type='application/x-www-form-urlencoded', referer=ref), err_type='ccbn'):
        # if not self.deal_result(self.execute('POST', url, data=payload, content_type='application/x-www-form-urlencoded'), err_type='ccbn'):
            return False
        data_list = self.parse()
        if not isinstance(data_list, list):
            return data_list
        pages = self.ret.get('msg').get('totalNum')
        if int(pages) > 10:
            for p in range(11, int(pages)+1, 10):
                payload['startNo'] = p
                if not self.deal_result(self.execute('POST', url, data=json.dumps(payload), referer=ref), err_type='ccbn'):
                    return False
                parse_res = self.parse()
                if not isinstance(parse_res, list):
                    return parse_res
                data_list.extend(parse_res)

        return data_list

    def parse(self):
        datas = self.ret.get('msg').get('myBankAccDetailList')
        data_list = []
        for d in datas:
            # if d.get('tranDate') == '2019-01-22':
            #     print(d)
            data = {}
            flag = d.get('dbCrFlag')
            am_key = 'creditAmount' if flag == 'C' else 'debitAmount'
            data['tranDate'] = '%s 00:00:00' % d.get('tranDate')
            data[am_key] = d.get('tranAmt')                 # (交易金额)
            data['balance'] = d.get('accBal')               # 余额
            data['summary'] = d.get('postscript')              # 摘要
            data['partyCompanyName'] = d.get('oppositeAccNm')   # 收(付)方名称
            data['partyAccount'] = d.get('oppositeAccNo')       # 收(付)方账号
            data['tranType'] = d.get('summary')              # 交易类型
            data['bankflowType'] = 2 if data.get('debitAmount') else 1
            account = d.get('accNo')
            our_company_name = d.get('accNm')
            data.update({'ourAccount': account, 'ourCompanyName': our_company_name})
            data['tranNo'] = d.get('tranNo')
            data['partyBankName'] = d.get('oppositeBankNm')                     # '收(付)方开户行:':
            data['tranTime'] = d.get('tranTime').replace(':', '')               # 交易时间
            create_time = time.strftime('%Y-%m-%d %H:%M:%S')
            data.update({'createTime': create_time, 'updateTime': create_time})
            data_list.append(data)
        return data_list

    def save(self, data):
        url = "http://erp.btomorrow.cn/adminjson/ERP_AddBankFlow"
        for dat in data:
            pay_or_get = 'creditAmount' if dat.get('creditAmount') else 'debitAmount'
            tran_time = dat.get('tranTime') if dat.get('tranTime') else ''
            sql = "INSERT INTO `t_bank_flow`(`createTime`, `updateTime`, `bankflowType`, `tranDate`, `tranTime`, " \
                  "`tranType`, `%s`, `ourAccount`, `ourCompanyName`, `balance`, `summary`, " \
                  "`tranNo`, `partyCompanyName`, `partyAccount`, `partyBankName`, `visable`)  " \
                  "SELECT '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','1' " \
                  "from DUAL where not exists (select tranNo from t_bank_flow where tranNo='%s');" % (
                      pay_or_get, dat.get('createTime'), dat.get('updateTime'), dat.get('bankflowType'), dat.get('tranDate'),
                      tran_time, dat.get('tranType'), dat.get(pay_or_get), dat.get('ourAccount'),
                      dat.get('ourCompanyName'), dat.get('balance'), dat.get('summary'), dat.get('tranNo'),
                      dat.get('partyCompanyName'), dat.get('partyAccount'), dat.get('partyBankName'),
                      dat.get('tranNo'))
            pay_load = {"opType": 1, "token": "dsjuei4mdnjklk2ldhjdldlanmdsajdhsajh", "sql": sql}
            self.headers = {'Content-Type': 'application/json'}
            res = self.execute('POST', url, data=json.dumps(pay_load), print_payload=False)
            if not res.get('succ'):
                logger.error(res.get('msg'))
            logger.info(sql)
            logger.info(res.get('msg').text)


def post_data(data, status_info):
    # post data and status
    print(data)
    json_data = {
        'json_str': data,
        'result_status': status_info
    }
    from requests import session
    session = session()
    url = 'http://erp.btomorrow.cn/adminjson/ERP_SaveCrawlerStatus'
    try:
        resp = session.post(url, data=json.dumps(json_data), timeout=10).json()
        logger.info(resp)
        if resp.get('errorCode') != 0:
            logger.info('结果上报失败: %s\n%s' % (json.dumps(data), status_info))
        logger.info('上报成功： %s' % (json_data))
    except Exception as ee:
        logger.error('server error', ee, exc_info=1)
    finally:
        session.close()


try:
    with open('ccbn_c.json', 'r') as f:
        ck_res = json.load(f)
except:
    ck_res = {}


def init_logger(spider):
    global logger
    log_path = os.path.abspath('./logs/ccbn')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    spider = 'ccbn_crawler' if not spider else spider
    logger = Util().record_log(log_path, spider) if not logger else logging.getLogger(spider)


def ccbn_run(spider=None, flag=1):
    """main entrance"""
    global ck_res
    init_logger(spider)
    # get login cookie
    if not ck_res:
        flag = 0            # 0 爬取错误，则报错, 1重试
        ck_res = get_task_parm({'un': 'tft125', 'pwd': '58452013'}, spider)
        if not ck_res.pop('succ'):
            # logger.critical('ccbn login failed after tried 3 times')
            return False
        with open('ccbn_c.json', 'w') as f:
            json.dump(ck_res, f)
    # init params
    bsn_code, cookie = ck_res.get('bsn_code'), ck_res.get('ccbn_cookie')
    headers = {
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Content-Type': "application/x-www-form-urlencoded",
        'Accept-Language': "zh-CN",
        'Cookie': cookie,
        'Host': "corp.bank.ecitic.com",
        'Referer': "https://corp.bank.ecitic.com/cotb/index.html",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    }

    # start crawler
    cc = CmbCrawler(bsn_code=bsn_code, headers=headers, spider=spider)
    res = cc.crawl_page_list()

    # post_res
    data = ck_res
    if res:
        post_data(data, status_info='0-成功')
    elif not res and flag == 1:
        ck_res = {}
        return ccbn_run(spider, flag=flag)
    else:
        return post_data(data, status_info='9999-失败')


if __name__ == '__main__':
    ccbn_run(spider='ccbn')

