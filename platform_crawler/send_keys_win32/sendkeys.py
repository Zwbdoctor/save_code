# _*_ coding:UTF-8 _*_
import win32api
import win32con
# import win32gui
from ctypes import windll, Structure, c_ulong, byref
from platform_crawler.send_keys_win32.key_code import VK_CODE_WIN
import time


class POINT(Structure):
    _fields_ = [("x", c_ulong), ("y", c_ulong)]


def get_mouse_point():
    po = POINT()
    windll.user32.GetCursorPos(byref(po))
    return int(po.x), int(po.y)


def mouse_click(x=None, y=None, left=True):
    if not x is None and not y is None:
        mouse_move(x, y)
        time.sleep(0.05)
    if left:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def mouse_wheel():
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -100)


def mouse_down(x=None, y=None, left=True):
    if not x is None and not y is None:
        mouse_move(x, y)
        time.sleep(0.05)
    if left:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    else:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def mouse_up(x=None, y=None, left=True):
    if not x is None and not y is None:
        mouse_move(x, y)
        time.sleep(0.05)
    if left:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def mouse_dclick(x=None, y=None):
    if not x is None and not y is None:
        mouse_move(x, y)
        time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def mouse_move(x, y):
    windll.user32.SetCursorPos(x, y)


def mouse_slip(x, w, h):
    """模拟鼠标滑动"""
    while True:
        x += 10
        y = x * (h/w)
        mouse_move(x, int(y))
        time.sleep(0.01)
        if x == w or y == h:
            break


def mouse_wheel_loop(wtimes):
    """滚轮翻页"""
    for e in range(wtimes):
        mouse_wheel()
        time.sleep(0.25)

def key_down(k):
    win32api.keybd_event(VK_CODE_WIN[k], 0, 0, 0)


def key_up(k):
    win32api.keybd_event(VK_CODE_WIN[k], 0, win32con.KEYEVENTF_KEYUP, 0)


def key_group(key_list):
    for k in key_list:
        key_down(k)
        time.sleep(0.05)
    for k in key_list:
        key_up(k)
        time.sleep(0.01)


def key_press(k):
    key_down(k)
    time.sleep(0.01)
    key_up(k)


def key_input(st='', press_sleep=0.01):
    special = {'!': ['shift', '1'], '@': ['shift', '2'], '#': ['shift', '3'], '$': ['shift', '4'], '%': ['shift', '5'],
               '^': ['shift', '6'], '&': ['shift', '7'], '*': ['shift', '8'], '(': ['shift', '9'], ')': ['shift', '0'],
               '_': ['shift', '-'], '+': ['shift', '='], '{': ['shift', '['], '}': ['shift', ']'], ':': ['shift', ';'],
               '"': ['shift', "'"], '|': ['shift', '\\'], '<': ['shift', ','], '>': ['shift', '.'], '?': ['shift', '/']}
    for c in st:
        if c in VK_CODE_WIN.keys():
            win32api.keybd_event(VK_CODE_WIN[c], 0, 0, 0)
            win32api.keybd_event(VK_CODE_WIN[c], 0, win32con.KEYEVENTF_KEYUP, 0)
        elif c in special.keys():
            key_group(special[c])
        elif c.isupper():
            key_group(['shift', c.lower()])
        time.sleep(press_sleep)


# if __name__ == "__main__":
#     key_group(['left_menu', 'up_arrow'])
#     key_group(['left_menu', 'down_arrow'])

    # mouse_click(100,100)
    # str1 = 'hello------'

    # key_input(str1)

    # x,y  = get_mouse_point()
    # fff = str(x) + "+" + str(y)
    # print fff

    # key_input(fff)

    # while (1):
    #     x, y = get_mouse_point()
    #     print(x, y)
    #     # key_input(str(x) + "-" + str(y))
    #     key_input(str(x) + str(y))
    #     time.sleep(2)

    #     if x < 10 and y < 10:
    #         break
    # key_input()

"""

"""
