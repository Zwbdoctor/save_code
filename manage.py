"""
    Spider Manage File
"""
import argparse
import socket
import os
import psutil
from multiprocessing import Process

from platform_crawler.test_special_account import run as test_run
from platform_crawler.spiders.pylib.kill_sth import kill_chrome_fscapture

_join = os.path.join
BASE_DIR = _join(os.path.dirname(__file__), 'platform_crawler')
try:
    with open(_join(BASE_DIR, 'configs', 'main.pid'), 'r') as pd:
        PID = pd.read()
except Exception:
    PID = None
# with open(_join(BASE_DIR, 'configs', 'task_type.txt'), 'r') as r:
#     CLIENT_NAME = r.read()


def open_task(func=None):
    global PID
    from platform_crawler.main import run as main_run
    if not func:
        func = main_run
    p = Process(target=func)
    p.start()
    PID = p.pid


def kill_task_process():
    global PID
    if PID:
        p = psutil.Process(pid=PID)
        p.kill()
    PID = None


def svn_update_with_dir_list(conn):
    msg = 'Please input the dir list based on (common) and split with ","'
    conn.sendall(msg.encode())
    print(f'>>: {msg}')
    # ................
    data = conn.recv(1024).decode().strip().split(',')      # dir list
    print(f'<<: {data}')
    svn_update(data)
    # ................
    msg = 'update OK'
    conn.sendall(msg.encode())
    print(f'>>: {msg}')


def svn_update(dir_name: list = None):
    if PID:     # 关闭任务
        p = psutil.Process(pid=PID)
        p.kill()
    name = f' {_join(BASE_DIR, *dir_name)}' if dir_name else ""
    cmd = f'svn update {name}'
    os.system(cmd)      # svn update
    open_task()         # 开启任务


def handle_pc():
    os.system('shutdown /r')


def restart_task():
    if PID:
        p = psutil.Process(pid=PID)
        p.kill()
    open_task()


def open_task_function():
    open_task(func=test_run)


def print_t() -> None: ...


urls = [
    ('1', open_task, 'task has been opend'),
    ('2', restart_task, 'task_process restart success'),
    ('3', handle_pc, 'PC will restart after 1 minutes'),
    ('4', kill_task_process, 'task spider has been killed'),
    ('5', svn_update, 'update ok'),
    ('6', open_task_function, 'test function opened'),
    ('7', kill_chrome_fscapture, 'chrome has been killed'),
    ('8', print_t, 'this is a msg of community test')
]


def url_handlers(conn, MSG):
    while True:
        data = conn.recv(1024).decode('utf-8')
        print(f'>>: {data}')
        if not data:
            print('client has disconnected')
            return
        elif data == '5.1':
            svn_update_with_dir_list(conn)
        for num, handler, msg in urls:
            if data == num:
                handler()
                conn.sendall(msg.encode())
                break
            elif data == '0':
                msg = 'bye'
                conn.sendall(msg.encode())
                break
        else:
            send_msg = f'Invalid choice! Please check and retry again\n{MSG}'
            print(f'<<: {send_msg}')
            conn.sendall(send_msg.encode())


def server():
    open_task()
    serv_addr = ('0.0.0.0', 8889)
    sock_serv = socket.socket()
    sock_serv.bind(serv_addr)
    sock_serv.listen(1)
    print('server start, waiting for connect...')
    while True:
        conn, adr = sock_serv.accept()
        print('a client connected ...')
        msg = '\n'.join([
            'Please choose the number of the choice:',
            '1.open task spider', '2.restart task_process', '3.restart PC', '4.kill task spider',
            '5.update svn(kill, update, restart)', '\t5.1 update with dir list',
            '6.open test_case script', '7.kill chrome browser', '8.community test',
            '0.disconnect'
        ])
        conn.sendall(msg.encode())
        print(f'<<: {msg}')
        url_handlers(conn, msg)
        conn.close()


def make_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start', help='start to run the manage server', action='store_true')
    parser.add_argument('-r', '--run_test', help='Run the test spider script', action='store_true')
    parser.add_argument('-t', '--task_process', help='start to run the task_process spider', action='store_true')
    parser.add_argument('-p', '--parse', help='send params to parse', action='store_true')

    args = parser.parse_args()
    if args.start:
        print('Start Server')
        server()
    elif args.run_test:
        print('start to run test scripts')
        test_run()
    elif args.task_process:
        from platform_crawler.main import run as main_run
        print('start to run task_process spider')
        main_run()
    elif args.parse:
        from platform_crawler.main import send_params_to_parse
        print('send params to parse')
        send_params_to_parse('QQ', 'shenchouhuihuangmingtian')
    else:
        print('None Params! Default start server')
        # server()
        test_run()


if __name__ == '__main__':
    try:
        make_parser()
    except:
        pass
    finally:
        if PID:
            with open(_join(BASE_DIR, 'configs', 'main.pid'), 'w') as p:
                p.write(PID)
