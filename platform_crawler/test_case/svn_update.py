"""

客户端
    采用socket连接
        发送 内容： （update, dir_name）
                    (restart) # 重启任务进程
服务端
    接收消息： 采用socket
        参数：
            （update, name=default_home_dir）
                os.chdir(default_home_dir)
                os.system(update_cmd)
             (restart)
                open(task.pid)
                p = Process(pid)
                p.kill()
                os.chdir(desktop)
                os.system(cm_start.bat)
"""
import socket
import os
import time
from multiprocessing import Process

PID = None


def open_task():
    global PID
    main_file_path = ''
    cmd = f'python3 {main_file_path}'
    os.system(cmd)
    p = Process(target=os.system, args=(cmd,))
    p.start()
    PID = p.pid


def server():
    serv_addr = ('127.0.0.1', 8889)
    sock_serv = socket.socket()
    sock_serv.bind(serv_addr)
    sock_serv.listen(1)
    print('server start, waiting for connect...')
    while True:
        conn, adr = sock_serv.accept()
        print('a client connected ...')
        # conn.sendall(f'hello {adr}'.encode())
        # print(f'>> hello {adr}, this is server')
        while True:
            data = conn.recv(1024).decode('utf-8')
            if data == 'bye':
                print(f'<<: {data}')
                conn.sendall('>>:bye'.encode())
            elif not data:
                print('client has disconnected')
                break
            else:
                print(f'<<:{data}')
                conn.sendall(input('>>:').encode())
        conn.close()


if __name__ == '__main__':
    server()
    # client()



