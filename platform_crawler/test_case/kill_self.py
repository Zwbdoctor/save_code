from multiprocessing import Process
import psutil
import time
import signal
import random
import os
from platform_crawler.utils.utils import Util
u = Util()
a = None
b = None

def child_worker(p):
    for e in range(10):
        print('child process: i am proc %s' % p)
        time.sleep(1)

def worker():
    logger = u.record_log(os.path.abspath('.'), 'kself')
    t = []
    for e in range(60):
        logger.info('worker: loop %s times' % e)
        p = Process(target=child_worker, args=(e,))
        p.start()
        t.append(p)
        time.sleep(1)
    for e in t:
        e.join()



def run():
    p = Process(target=worker)
    # p.daemon = True
    p.start()
    p.join(timeout=3)
    print('main run: timeout after 5 seconds')
    print('child pid: %s' % p.pid)
    child_process = psutil.Process(p.pid).children()
    print(child_process)
    p.terminate()
    print('i will still run 1 times')
    print(os.getpid())

def change_glo():
    global a, b
    a = 1
    b = 2
    print(a,b)

if __name__ == '__main__':
    # run()
    change_glo()