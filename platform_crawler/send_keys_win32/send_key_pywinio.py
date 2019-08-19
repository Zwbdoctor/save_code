import pywinio
import time
import atexit

from platform_crawler.send_keys_win32.winio_key_code import VK_CODE

# KeyBoard Commands
# Command port
KBC_KEY_CMD = 0x64
# Data port
KBC_KEY_DATA = 0x60

__winio = None


def __get_winio():
    global __winio

    if __winio is None:
        __winio = pywinio.WinIO()

        def __clear_winio():
            global __winio
            __winio = None

        atexit.register(__clear_winio)

    return __winio


def wait_for_buffer_empty():
    '''
    Wait keyboard buffer empty
    '''

    winio = __get_winio()

    dwRegVal = 0x02
    while (dwRegVal & 0x02):
        dwRegVal = winio.get_port_byte(KBC_KEY_CMD)


def key_down(scancode):
    winio = __get_winio()

    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_CMD, 0xd2)
    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_DATA, scancode)


def key_up(scancode):
    winio = __get_winio()

    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_CMD, 0xd2)
    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_DATA, scancode | 0x80)


def key_press(scancode, press_time=0.5):
    key_down(scancode)
    time.sleep(press_time)
    key_up(scancode)


def key_upper(scancode_group, press_time=0.5):
    sec = []
    for k in scancode_group:
        key_down(VK_CODE[k])
        sec.append(k)
        time.sleep(press_time)
    for k in sec:
        key_up(VK_CODE[k])
        time.sleep(0.1)


def key_input(st=''):
    for c in st:
        try:
            if c.isupper():
                key_upper(['shift', c.lower()])
            else:
                key_press(VK_CODE[c])
        except:  # 符号
            key_press(VK_CODE[c])
        time.sleep(0.5)


def key_group(key_list):
    for k in key_list:
        if len(k) > 1:
            key_press(VK_CODE[k])
        elif k.isupper():
            key_upper(['shift', k])
        else:
            key_press(VK_CODE[k])


def key_input_upper(st=''):
    for c in st:
        try:
            key_press(VK_CODE[c])
            time.sleep(0.5)
        except:
            key_press(0x3A)
            time.sleep(0.5)
            key_press(VK_CODE[c.lower()])
            key_press(0x3A)


# Press 'A' key
# Scancodes references : https://www.win.tue.nl/~aeb/linux/kbd/scancodes-1.html

if __name__ == '__main__':
    s = 'd__--dfFASsgsSDF___asdfwe234262'
    time.sleep(3)
    for e in range(10):
        key_input(st=s)
        time.sleep(2)

"""
Windows 以阻止安装未具有数字签名的驱动程序。请卸载使用该驱动程序的程序或设备，并在其发行商网站商查找数字签名的驱动程序版本。
ddfFASsgsSDF
"""
