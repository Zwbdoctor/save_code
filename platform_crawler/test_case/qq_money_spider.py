"""
Attention:
    !!! 图片缓存文件目录，需手动设置
"""
from time import sleep, time
from threading import Thread
import json
import os

from platform_crawler.utils.post_get import post
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.kill_sth import stop_thread, kill_chrome_fscapture   # , clean_desk


spider_type = {}

from platform_crawler.spiders.CPA.qq_finacial_spider import QQFinancialSpider


get_task_url = 'http://erp.btomorrow.cn/adminjson/ERP_PubishCrawlerTask'
u = Util()
sd_path = os.path.abspath('./save_data')
log_path = os.path.abspath('./logs')
logger = u.record_log(log_path, 'YYBHLCPD')


# record the process id
pid = os.getpid()
with open('cm_main.pid', 'w') as pd:
    pd.write(str(pid))


# Run task process with a thread so that it could be strongly killed when it was running timeout
def run_process(task_name, args=None):
    args = args if args else ()
    task_object = task_name()                  # 创建任务对象
    task_func = task_object.run_task      # 指定要执行的函数入口
    p = Thread(target=task_func, args=(args,))
    start_time = time()
    kill_chrome_fscapture()
    p.start()
    p.join(timeout=60*10)
    if int(time())-start_time > 60 * 10:        # 超时，强行关闭
        stop_thread(p)
        res = kill_chrome_fscapture()
        logger.info(res.get('msg'))
        logger.critical('spider running timeout after 20 minutes')
    else:
        del(p)
        del(task_object)


# main entrance function
def get_task():
    global icbc_last_time
    while True:
        # 获取任务
        data = {'platformType': 'python'}
        ret = post(get_task_url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, timeout=60)
        if not ret['is_success']:
            # 请求失败
            logger.warning('get task failed')
            sleep(60)
            continue
        else:
            # 请求成功
            logger.debug('from task_api:\n'+ret['msg'].content.decode())
            try:
                um = json.loads(ret['msg'].content)
            except:
                sleep(30)   # 服务器error
                continue
            if um['errorCode'] == 8:            # 没有任务
                sleep(5)
                continue
            elif um['errorCode'] == 0:          # 得到任务
                if um['body']['platform'] in spider_type.keys():
                    # acc = ['859248274@qq.com', '1434653746@qq.com', 'liling7@guazi.com', '2745358874']        # 指定账号
                    # if um['body']['account'] not in acc:                                                      # 执行任务
                    #     continue
                    if um.get('body').get('platform') not in ['qq_finance']:  #, 'WIFIKEY']:
                        sleep(0.5)
                        continue
                    logger.info('task info:')
                    logger.info(um)

                    # 执行任务
                    try:
                        # spider_type[um['body']['platform']].run_task(um['body'])
                        run_process(task_name=spider_type.get(um.get('body').get('platform')), args=um.get('body'))
                    except Exception as e:
                        logger.error(e, exc_info=1)
                        # 发送告警
                        logger.critical(e, exc_info=1)
                    sleep(5)
                else:
                    sleep(2)
                continue
            else:
                logger.error('task server error')
                sleep(5)


data = {'platform': 'qq_finance', 'account': None, 'password': None}  # , 'dates': (2018, 8, 2018, 8)}

rec_path = os.path.join(os.path.abspath('./save_data'), 'xlsx_files', 'accts.json')
try:
    with open(rec_path, 'r') as s:
        has_rec = json.load(s)
except:
    has_rec = {'YYBHLCPD': [], 'YYBSYH': [], 'GDT': []}


def run():
    global has_rec, data
    # 0-ok, 1-not ok
    accs_path = os.path.join(os.path.abspath('./save_data'), 'xlsx_files', 'cpd_accounts.csv')
    err_list = []
    with open(accs_path, 'r') as f:
        accts = f.readlines()
    for i in list(set(accts)):
        plat, acct, pwd = i.split(',')
        if acct in has_rec[plat]:
            logger.info('pass')
            continue
        data = {'account': acct, 'platform': plat, 'password': pwd.strip()}
        qq_finance = QQFinancialSpider
        try:
            qq_finance(data).run_task(data)
        except Exception as er:
            logger.error(er, exc_info=1)
            err_list.append([plat, acct, pwd])
            logger.warning([plat, acct, 'get flow failed'])
            continue
        has_rec[plat].append(acct)
        del(qq_finance)
        with open(rec_path, 'w') as s:
            json.dump(has_rec, s)
    else:
        logger.error(err_list)


if __name__ == '__main__':
    while True:
        try:
            run()
            break
        except Exception as ea:
            logger.error(ea, exc_info=1)
            with open(rec_path, 'w') as s:
                json.dump(has_rec, s)
            break
        except KeyboardInterrupt:
            print('stop with KeyboardInterrupt!!!')
            with open(rec_path, 'w') as s:
                json.dump(has_rec, s)
            break
