import os
from pyautogui import screenshot


join = os.path.join
BASEDIR = os.path.dirname(__file__).replace('/', '\\')
sd_path = join(BASEDIR, 'save_data')
LOGPATH = join(BASEDIR, 'logs')
IMG_PATH = join(BASEDIR, 'imgs')
temp_path = join(BASEDIR, 'img_temp')
conf_path = join(BASEDIR, 'configs')
conf_file_path = join(conf_path, 'config_file.json')
task_type_path = join(conf_path, 'task_type.txt')
use_time_dir_name = join(sd_path, 'task_use_time')
JS_PATH = join(BASEDIR, 'utils', 'JS')
BAL_PATH = join(sd_path, 'balance_data')

paths = [sd_path, LOGPATH, temp_path, IMG_PATH, conf_path, use_time_dir_name, BAL_PATH]

# default verify path
DEFAULT_VERIFY_PATH = join(IMG_PATH, 'vc.png')


class GlobalVal:

    __slots__ = ['err_src_name']

    # LOG
    CUR_MAIN_LOG_NAME = 'default'

    # task type
    CUR_TASK_TYPE = None

    # destination directory
    DST_DIR = None


class GlobalFunc:

    @classmethod
    def save_screen_shot(cls, img_name):
        screenshot(img_name)
