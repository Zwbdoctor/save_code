"""
Attention:
    !!! 图片缓存文件目录，需手动设置
# ------ record pid
pid = os.getpid()
with open('cm_main.pid', 'w') as pd:
    pd.write(str(pid))
spider_type = {}
"""
from time import sleep, time, strftime
from threading import Thread
from pyautogui import click
import json
import csv

from platform_crawler.utils.post_get import post
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.kill_sth import stop_thread, kill_chrome_fscapture, kill_process_with_args       # , clean_desk
from platform_crawler.spiders.pylib.post_res import post_res
from platform_crawler.settings import *
from . import class_register, import_source


# class register

get_task_url = 'http://erp.btomorrow.cn/adminjson/ERP_PubishCrawlerTask'
u = Util()
spider_type = class_register()
header_row, use_time_list, write_time, task_type, pc_name = ['', '', '', '', '']

# init logs and savedata dirs
try:
    for f in paths:
        if not os.path.exists(f):
            os.makedirs(f)
except Exception as e:
    from traceback import print_exc
    print_exc(e)

logger = None


# Run task process with a thread so that it could be strongly killed when it was running timeout
def run_process_with_multiprocessing(task_name, args=None):
    args = args if args else ()
    # 创建任务对象
    if args.get('platform') in ['UC', 'SLY', 'ZYInput', 'TTX', '2345', 'JRTT']:
        task_object = task_name(args)
    else:
        task_object = task_name()
    task_func = task_object.run_task      # 指定要执行的函数入口
    p = Thread(target=task_func, args=(args,))
    start_time = time()
    kill_chrome_fscapture()
    p.start()
    p.join(timeout=60*30)
    res = kill_chrome_fscapture()
    if int(time())-start_time > 60 * 30:        # 超时，强行关闭
        stop_thread(p)
        kill_chrome_fscapture()
        logger.info(res.get('msg'))
        logger.error('spider running timeout after 20 minutes')
    else:
        del(p)
        del(task_object)


def send_params_to_parse(platform, account):
    # date = strftime('%Y-%m-%d')
    data = {"platform": platform, 'account': account}
    test_url = 'http://erp.btomorrow.cn/adminjson/ERP_AnalysisCPA'
    ret = post(test_url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, timeout=60)
    if not ret.get('is_success'):
        logger.error(ret.get('msg').text)
    logger.info(f'parser | {ret.get("msg").text}')


# run task function
def run_process(platform, data):
    global use_time_list
    task_object = None
    try:
        task_object = import_source(*spider_type.get(platform))(data)
        st = time()                             # start time
        logger.info('start to run task: \n%s' % data)
        # run task
        res = task_object.run_task(data)
        # time record
        if not res:
            logger.info('task error')
            return False
        time_duration = round(time()-st, 2)
        use_time_row = [platform, data.get('account'), time_duration]
        use_time_list.append(use_time_row)
        logger.info('task done, use time: %s' % time_duration)
        send_params_to_parse(platform, data.get('account'))
        click(800, 10)
        return True
    except Exception as e:
        logger.error(e, exc_info=1)
        return False
    finally:
        kill_process_with_args('chrome', 'TIM')
        del(task_object)
        sleep(1)


def immediate():
    """
    config: {'immediate': [platform, data]}
    :return:
    """
    try:
        with open(conf_file_path, 'r') as cfr:
            config = json.load(cfr)
    except:
        config = {}
    if config.get('immediate'):
        # 执行任务
        platform, data = config.pop('immediate')
        data['id'] = 1275
        run_process(platform, data)
        # if run_process(platform, data):
        with open(conf_file_path, 'w') as cfw:
            json.dump(config, cfw)


def init_():
    global header_row, use_time_list, write_time, task_type, pc_name, logger
    logger = u.record_log(LOGPATH, 'main')
    # init timer
    use_time_file_name = join(use_time_dir_name, f'{strftime("%Y-%m-%d")}.csv')
    try:
        with open(use_time_file_name, 'r', encoding='utf-8') as cf:
            reader = csv.reader(cf)
            header_row = next(reader)
            use_time_list = list(reader)
    except:
        use_time_list = []
        header_row = ['platform', 'account', 'use_time']
    write_time = time()

    # init task_type
    try:
        with open(task_type_path, 'r', encoding='utf-8') as tp:
            task_type = tp.read().strip()
        pc_name = task_type
        task_type = 'MSG' if task_type == 'MSG2' else task_type
    except:
        logger.error(f'Not found file:{task_type_path}, Please check and try again')


# 任务计时器
def timer():
    global write_time
    use_time_file_name = join(use_time_dir_name, f'{strftime("%Y-%m-%d")}.csv')
    with open(use_time_file_name, 'w', newline='', encoding='utf-8') as cfw:
        writer = csv.writer(cfw)
        writer.writerow(header_row)
        writer.writerows(use_time_list)
    write_time = time()


# get task function
def get_task():
    global task_type
    # 获取任务
    data = {'platformType': task_type, 'flag': pc_name}
    ret = post(get_task_url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, timeout=60)
    if not ret['is_success']:
        # 请求失败
        logger.error('get task failed')
        sleep(60)
        return False
    else:
        # 请求成功
        try:
            um = ret['msg'].json()
            logger.debug('from task_api:\n%s' % um)
        except:
            sleep(30)   # 服务器error
            logger.error('server error')
            return False
        if um['errorCode'] == 8:            # 没有任务
            print('none task')
            task_type = 'MSG' if task_type in 'CPA' else 'CPA'
            sleep(60)
            return False
        elif um['errorCode'] == 0:          # 得到任务
            data = um.get('body')
            return data
        else:
            logger.error('task server error')
            sleep(5)
            return False


def task_filter(data):
    platform, account, imd = data.get('platform'), data.get('account'), data.get('immediate')
    if platform not in spider_type.keys():      # 是否注册
        sleep(0.5)
        return {'suc': False}
    if imd == 0:                                # 立即执行
        with open(conf_file_path, 'w') as cfw:
            json.dump({'immediate': [platform, data]}, cfw)
    acc = []          # 指定账号
    # acc.extend(['168彩票'])          # 指定账号
    err_account = []
    pass_platform = ['MEIZUSTORE', 'HUAWEISTORE', 'OPPOSTORE', 'GDT']
    today = strftime('%d')
    if int(today) == 3:
        pass_platform.remove('GDT')
    if account in acc:      # 跳过指定账号
        params = [data.get('id'), account, platform, '', 3]
        post_res(*params)
        sleep(2)
        return {'suc': False}
    if account in err_account:      # 确定错误的账号直接上报结果
        params = [data.get('id'), account, platform, '', 4]
        post_res(*params)
        sleep(2)
        return {'suc': False}
    if platform in pass_platform:       # 跳过每月手动爬取的平台
        params = [data.get('id'), account, platform, '', 3]
        post_res(*params)
        return {'suc': False}
    return {'suc': True, 'data': [platform, data]}


def loop_run():
    global task_type
    while True:
        # 00:00 ~ 01:00 不执行爬虫任务
        hours, minutes = strftime('%H:%M').split(':')
        if int(hours) < 1 and int(minutes) < 58:
            if int(minutes) in [4, 5]:        # 凌晨恢复当前爬取任务类型
                init_()
            sleep(30)
            continue
        # 记录任务执行时长(一小时一次)
        if int(time() - write_time) > 3600:
            timer()
        # 需要立即执行的任务
        immediate()
        # 获取任务
        task = get_task()
        if not task:
            continue
        # 过滤任务
        task = task_filter(task)
        if not task.get('suc'):
            continue
        # 执行任务
        platform, data = task.get('data')
        run_process(platform, data)


def run():
    init_()
    while True:
        try:
            loop_run()
            sleep(60*3)
        except Exception as ea:
            logger.error(ea, exc_info=1)
            # logger.critical(ea, exc_info=1)
            timer()
            sleep(1)
        except KeyboardInterrupt:
            print('stop with KeyboardInterrupt!!!')
            timer()
            break


if __name__ == '__main__':
    # run()
    send_params_to_parse('QQ', 'shenchouhuihuangmingtian')
