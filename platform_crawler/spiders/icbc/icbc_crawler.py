import time
import logging
import os
import json
# import re

from platform_crawler.utils.utils import Util
from platform_crawler.spiders.icbc.compare_bill_crawlers import CompareBillCrawlers
from platform_crawler.spiders.icbc.history_list_crawlers import HistoryCrawlers
from platform_crawler.spiders.icbc.ebill_crawlers import EbillCrawlers
from platform_crawler.spiders.icbc.icbc_base_crawler import BaseCrawler

logger = None
log_name = None


class IcbcCrawlers(BaseCrawler):

    def __init__(self, icbc_sessionId, icbc_cookie, base_headers=None):
        self.icbc_sessionid = icbc_sessionId
        self.icbc_cookie = icbc_cookie
        self.headers = base_headers
        self.headers['Cookie'] = icbc_cookie
        super().__init__(headers=base_headers, spider=log_name)

    def crawler_and_save(self):
        year, this_month, today = time.strftime('%Y-%m-%d').split('-')
        if int(today) < 5:
            day_len = Util().mDays(int(year), int(this_month)-1)
            day = str(day_len-5-int(today))
        else:
            day = str(int(today)-5)
        month = str(int(this_month)-1) if int(today) < 5 else this_month
        first_date = '%s-%s-%s' % (year, month, day)
        last_date = '%s-%s-%s' % (year, month, today)
        return self.crawler(first_date, last_date)

    def fill_bank_flow(self, cbc_list=None, history_list=None, ebill_list=None):
        """build the bank_flow json"""
        # with open('bank_flow.json', 'r') as f:
        #     data = json.load(f).get('data')
        # cbc_list, history_list, ebill_list = data[0], data[1], data[2]
        # 对应依据：日期，账号，户名     (借:支持2，贷：收入1)
        n = 0
        for h in history_list:
            hmoney = h.get('Transaction_amount').replace(',', '').strip()
            hdate = h.get('date_record').replace('-', '')
            create_time = time.strftime('%Y-%m-%d %H:%M:%S')
            tran_type = 1 if h.get('tran_type') == '贷' else 2
            tran_key = 'creditAmount' if tran_type == 1 else 'debitAmount'
            dat = {'createTime': create_time, 'updateTime': create_time, 'bankflowType': tran_type, 'tranDate': '%s 00:00:00' % h.get('date_record'),
                   'summary': h.get('digest'), tran_key: hmoney}
            if not h.get('detail_content')[0].get('msg'):
                # 有回单页面
                detail = h.get('detail_content')
                pay_name, pay_account, get_account, get_name = None, None, None, None
                for e in detail:
                    if e.get('name') == '时间戳':
                        dat['tranTime'] = ''.join(e.get('value').split('-')[-1].split('.')[:-1])
                    elif e.get('name') == '业务（产品）种类':
                        dat['tranType'] = e.get('value')

                    elif e.get('name') == '收款账号':
                        get_account = e.get('value')
                    elif e.get('name') == '收款户名':
                        get_name = e.get('value')

                    elif e.get('name') == '业务流水号':
                        dat['tranNo'] = e.get('value')

                    elif e.get('name') == '付款户名':
                        pay_name = e.get('value')
                    elif e.get('name') == '付款账号':
                        pay_account = e.get('value')
                    if tran_type == 2:
                        dat.update({'ourAccount': pay_account, 'ourCompanyName': pay_name, 'partyCompanyName': get_name, 'partyAccount': get_account})
                    else:
                        dat.update({'ourAccount': get_account, 'ourCompanyName': get_name, 'partyCompanyName': pay_name, 'partyAccount': pay_account})
            else:
                # 没有回单信息，需要另外查询
                e = None
                for e in ebill_list:
                    edate, etran_type, emoney, edigest, tranType, tranTime, tranNo = None, None, None, None, None, None, None
                    for ed in e.get('detail_content'):
                        if ed.get('name') == '记账日期':
                            edate = ed.get('value').replace('年', '').replace('月', '').replace('日', '')
                        elif ed.get('name') == '借贷标志':
                            etran_type = ed.get('value')
                        elif ed.get('name') == '金额':
                            emoney = ed.get('value').replace('元', '').replace(',', '').strip()
                        elif ed.get('name') == '摘要':
                            edigest = ed.get('value')

                        elif ed.get('name') == '主机时间戳':
                            tranTime = ''.join(ed.get('value').split('-')[-1].split('.')[:-1])
                        elif ed.get('name') == '业务（产品）种类':
                            tranType = ed.get('value')
                        # elif ed.get('name') == '余额':
                            # balance = ed.get('value').replace('元', '').replace(',', '').strip()
                        elif ed.get('name') == '交易流水号':
                            tranNo = ed.get('value')

                    upd = {
                        'ourAccount': e.get('our_account'), 'ourCompanyName': e.get('our_account_name'),
                        'partyCompanyName': e.get('rec_account_name'), 'partyAccount': e.get('rec_account'),
                        'tranTime': tranTime, 'tranType': tranType, 'tranNo': tranNo,
                    }
                    if not h.get('rec_account'):
                        if (h.get('unit_name') == e.get('rec_account_name')) and (edate == hdate) \
                                and (etran_type == h.get('tran_type')) and (emoney == hmoney) and (edigest == h.get('digest')):
                            dat.update(upd)
                            break
                    else:
                        if (h.get('unit_name') == e.get('rec_account_name')) and (edate == hdate) and (etran_type == h.get('tran_type')) \
                                and (emoney == hmoney) and (edigest == h.get('digest')) and (h.get('rec_account') == e.get('rec_account')):
                            dat.update(upd)
                            break
            for cl in cbc_list:
                cmoney = cl.get('lend_money_num') if cl.get('income_num') == '0.00' else cl.get('income_num')
                cmoney = cmoney.replace(',', '')
                balance = cl.get('balance').replace(',', '')
                if not h.get('rec_account'):
                    if ((cl.get('date').replace('-', '') == hdate) and (cl.get('dest_name') == h.get('unit_name')) and (cmoney == hmoney)):
                        dat['balance'] = balance
                        break
                else:
                    if ((cl.get('date').replace('-', '') == hdate) and cl.get('dest_account') == h.get('rec_account')
                            and (cl.get('dest_name') == h.get('unit_name')) and (cmoney == hmoney)):
                        dat['balance'] = balance
                        break
            # logger.info(dat)
            n += 1
            self.save(dat)
        else:
            logger.info('whole nums: ------------ %s' % n)

    def save(self, dat):
        url = "http://erp.btomorrow.cn/adminjson/ERP_AddBankFlow"
        pay_or_get = 'creditAmount' if dat.get('creditAmount') else 'debitAmount'
        if dat.get('tranNo') == '00000000':
            dat['tranNo'] = 'hhmt%(tranDate)s%(tranTime)s%(money)s' % {
                'tranDate': dat.get('tranDate').split(' ')[0], 'tranTime': dat.get('tranTime'), 'money': dat.get(pay_or_get)
            }
        sql = "INSERT INTO `t_bank_flow`(`createTime`, `updateTime`, `bankflowType`, `tranDate`, `tranTime`, " \
              "`tranType`, `%s`, `ourAccount`, `ourCompanyName`, `balance`, `summary`, `tranNo`, `partyCompanyName`, " \
              "`partyAccount`, `visable`) SELECT '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'" \
              "from DUAL where not exists (select tranNo from t_bank_flow where tranNo='%s');" % (
            pay_or_get, dat.get('createTime'), dat.get('updateTime'), dat.get('bankflowType'), dat.get('tranDate'), dat.get('tranTime'),
            dat.get('tranType'), dat.get(pay_or_get), dat.get('ourAccount'), dat.get('ourCompanyName'), dat.get('balance'),
            dat.get('summary'), dat.get('tranNo'), dat.get('partyCompanyName'), dat.get('partyAccount'), 1, dat.get('tranNo'))

        pay_load = {"opType": 1, "token": "dsjuei4mdnjklk2ldhjdldlanmdsajdhsajh", "sql": sql}
        self.headers = {'Content-Type': 'application/json'}
        res = self.execute('POST', url, data=json.dumps(pay_load), print_payload=False)
        if not res.get('succ'):
            logger.error(res.get('msg'))
        logger.info(sql)
        logger.info(res.get('msg').text)

    def crawler(self, first_date, last_date):
        logger.info('sessionID: %s ----initCookie: %s ----- DateRange: %s~%s' % (
            self.icbc_sessionid, self.icbc_cookie, first_date, last_date))

        cbc = CompareBillCrawlers(self.icbc_sessionid, self.icbc_cookie, headers=self.headers, spider='%s.cbc_crawler' % log_name)    # 电子对账单
        cbc_list = cbc.crawler_and_save(first_date, last_date)
        if not cbc_list.get('succ'):
            logger.error(cbc_list.get('msg'))
            return cbc_list
        logger.info(str(len(cbc_list.get('data'))))

        history = HistoryCrawlers(self.icbc_sessionid, self.icbc_cookie, headers=self.headers, spider='%s.hc_crawler' % log_name)     # 历史明细
        history_list = history.crawler_and_save(first_date, last_date)
        if not history_list.get('succ'):
            logger.error(history_list.get('msg'))
            return history_list
        logger.info('history_length: %s' % str(len(history_list.get('data'))))

        ebill = EbillCrawlers(self.icbc_sessionid, self.icbc_cookie, headers=self.headers, spider='%s.eb_crawler' % log_name)         # 回单
        ebill_list = ebill.crawler_and_save(first_date, last_date)
        if not ebill_list.get('succ'):
            logger.error(ebill_list.get('msg'))
            return ebill_list
        logger.info(str(len(ebill_list.get('data'))))
        # data = {'data': [cbc_list.get('data'), history_list.get('data'), ebill_list.get('data')]}
        # with open('bank_flow.json', 'w') as f:
        #     json.dump(data, f)
        self.fill_bank_flow(cbc_list.get('data'), history_list.get('data'), ebill_list.get('data'))           # 拼接流水数据


def icbc_run(spider, icbc_sid=None, icbc_cks=None):
    global logger, log_name
    # log_name = '%s.icbc' % spider
    logger = logging.getLogger(log_name)
    log_path = os.path.abspath('.')
    logger = Util().record_log(log_path, spider)
    # icbc_sid = "EKCYDJDUGREDIDJVCOEJENISJGFGHMDMDWHLJIHC"
    # icbc_cks = "ar_stat_ss=4936397698_7_1540807848_9999; ar_stat_uv=31490953308686463371|9999; SRV_EBANKC_PUJI=rs8|W9ZsK|W9ZmF"
    headers = {
        "Accept": "text/html, application/xhtml+xml, image/jxr, */*",
        "Referer": "https://corporbank-simp.icbc.com.cn/ebankc/newnormalbank/include/leftframe.jsp?dse_sessionId=" + icbc_sid
                   + "&chain=E19%7C%E8%B4%A6%E6%88%B7%E7%AE%A1%E7%90%86",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Host": "corporbank-simp.icbc.com.cn",
        "Cookie": None,
    }
    c = IcbcCrawlers(icbc_sid, icbc_cks, base_headers=headers)
    c.crawler_and_save()


if __name__ == '__main__':
    # while True:
    icbc_run('icbc')

