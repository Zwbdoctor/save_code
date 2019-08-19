"""
    :s#vivian/#sky/# 替换当前行第一个 vivian/ 为 sky/

    :%s+/oradata/apras/+/user01/apras1+ （使用+ 来 替换 / ）： /oradata/apras/替换成/user01/apras1/
        args = {
            'hhStr': 'do1960',
            'dateStr': '2018-11-29',
            'id': 1,
            'account': 'zhonglijuan@btomorrow.cn',
            'channelId': 1147
        }
        url = 'http://erp.btomorrow.cn/adminjson/ERP_TestCrawler'

        res = post(url, data=json.dumps(args), headers={"Content-Type": "application/json"})
        print(res.get('msg').text)
"""
from platform_crawler.spiders.pylib.kill_sth import kill_process_with_args
import json
import time
import csv
import os
import traceback

from platform_crawler.settings import sd_path

today = time.strftime('%d')
try:
    with open('./completed.json', 'r') as fr:
        completed = json.load(fr)
    if completed.get('today') != today:
        completed = {'today': today, 'acct': []}
except:
    completed = {'today': today, 'acct': []}

# from platform_crawler.configs.app_main_config import platform_filter

# init timer
use_time_file_name = os.path.join(sd_path, 'task_use_time_%s.csv' % (time.strftime('%Y-%m-%d')))
try:
    with open(use_time_file_name, 'r') as cf:
        reader = csv.reader(cf)
        header_row = next(reader)
        use_time_list = list(reader)
except:
    use_time_list = []
    header_row = ['platform', 'account', 'use_time']
write_time, write_flag = time.time(), False


# run task function
def run_process(task_object, data):
    try:
        st = time.time()   
        # run task
        res = task_object.run_task(data)
        # time record
        if not res:
            return False
        return True
    except Exception:
        return False
    finally:
        kill_process_with_args('chrome', 'TIM')
        del(task_object)
        time.sleep(1)


# 任务计时器
def timer():
    global write_time
    with open(use_time_file_name, 'w', newline='') as cfw:
        writer = csv.writer(cfw)
        writer.writerow(header_row)
        writer.writerows(use_time_list)
    write_time = time.time()


def run_from_file():
    global completed
    with open('./task_acct.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        ull = list(reader)
    err_list = []
    for ui in ull:
        if not ui:
            continue
        aid, category, plat, acct, password, login_url = ui
        ui = {'id': aid, 'category': category, 'account': acct, 'password': password, 'platform': plat, 'loginUrl': login_url.strip()}
        if aid in completed.get('acct'):
            print('pass completed')
            continue
        if plat not in platform_filter:
            continue
        task_object = spider_type.get(ui.get('platform'))(ui)
        # task_object.run_task(ui)
        result = yield task_object, ui
        if result:
            completed['acct'].append(aid)
            with open('./completed.json', 'w') as fw:
                json.dump(completed, fw)
        else:
            err_list.append(aid)
    else:
        with open('./uncompleted.json', 'w', encoding='utf-8') as unf:
            json.dump(err_list, unf)


def run():
    task_gen = run_from_file()
    spider, data = next(task_gen)
    while True:
        # 记录任务执行时长(一小时一次)
        if int(time.time() - write_time) > 3600:
            timer()
        # 执行任务任务生成器
        res = run_process(spider, data)
        # 任务生成器
        spider, data = task_gen.send(res)


if __name__ == '__main__':
    try:
        run()
    except StopIteration:
        print('done')
    except Exception:
        with open('./completed.json', 'w') as fw:
            json.dump(completed, fw)
        timer()
        traceback.print_exc()
    except KeyboardInterrupt:
        timer()