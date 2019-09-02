from inspect import isclass
from ctypes import c_long, pythonapi, py_object
from psutil import process_iter
import psutil
from platform_crawler.settings import join, IMG_PATH
import os


def open():
    psutil.Popen()


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = c_long(tid)
    if not isclass(exctype):
        exctype = type(exctype)
    res = pythonapi.PyThreadState_SetAsyncExc(tid, py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def kill_process_with_args(*kill_list):
    try:
        for e in process_iter():
            for k in kill_list:
                if k in e.name():
                    os.system(f'taskkill /PID {e.pid}')
                    # e.kill()
    except:
        pass


def kill_chrome_fscapture(banks=False, explorer=False):
    if explorer:
        # fp = r'C:/Windows/explorer.exe'
        for p in process_iter():
            if 'explorer' in p.name():
                p.kill()
                break
        # Popen([fp])
        return True
    kill_list = ['chrome']  #, 'FSCapture']    
    try:
        for e in process_iter():
            if banks:
                kill_list.extend(['iexplore', 'IEDriverServer'])
            for kl in kill_list:
                if kl in e.name():
                    # e.kill()
                    os.system(f'taskkill /PID {e.pid} /F')
                    return {'succ': True, 'msg': 'killed proc: %s' % e.name}
    except:
        return 'no chrome or FSCapture running, skip this step'


# clean the window of teamview's end window
def clean_desk(u):
    is_tmv = join(IMG_PATH, 'clean_desk', 'tv_enter.png')
    click_enter = join(IMG_PATH, 'clean_desk', 'zan.png')
    if u.btn_location(is_tmv, loop_time=3):
        res = u.btn_location(click_enter)
        if res:
            u.click_point(res[0] + 102, res[1])
    return True


if __name__ == '__main__':
    kill_chrome_fscapture(explorer=True)
