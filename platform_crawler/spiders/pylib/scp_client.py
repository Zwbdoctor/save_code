import os
import logging
from time import strftime

from platform_crawler.utils.scp_tool import RemoteShell
from platform_crawler.settings import GlobalVal, BASEDIR

logger = None


def init_dst_dir(platform, is_cpa=False):
    """初始化，父目录"""
    global logger
    logger = logging.getLogger(GlobalVal.CUR_MAIN_LOG_NAME)
    cudate = strftime('%Y-%m-%d')
    if not is_cpa:
        dst_path = '/data/python/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    else:
        dst_path = '/data/python/CPA/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    t = RemoteShell()
    test_host = '47.100.120.114'
    t2 = RemoteShell(host=test_host)
    local_path = os.path.join(BASEDIR, 'init_dir')
    put(t, t2, local_path, dst_path)
    del(t, t2)
    logger.info(f'PLATFORM:{platform} | LOCAL_PATH:./init_dir | DST_PATH:{dst_path}')
    return {'succ': True}


def put(t1, t2, dir_path, dst_path, isdir=True):
    """执行上传"""
    err_list = []
    for x in [t1, t2]:
        res, err = x.upload(dir_path, dst_path, isdir=isdir)
        if not res:
            logger.error(err, exc_info=1)
            err_list.append(1)
    return True if len(err_list) == 0 else False


def upload_file(dir_path, platform, is_cpa=False):
    """初始化上传步骤"""
    cudate = strftime('%Y-%m-%d')
    if not is_cpa:
        dst_path = '/data/python/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    else:
        dst_path = '/data/python/CPA/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    files = os.listdir(dir_path)
    if not files:
        return True
    t = RemoteShell()
    t2 = RemoteShell(host='47.100.120.114')          # test env
    res = put(t, t2, dir_path, dst_path)
    if not res:
        logger.error(f'Upload failed with the path: {dst_path}')
    logger.info(f'PLATFORM:{platform} | LOCAL_PATH:{dir_path} | DST_PATH:{dst_path}')
    return res


def upload_balance(dir_path, dst_path):
    t = RemoteShell()
    t2 = RemoteShell(host='47.100.120.114')          # test env
    res = put(t, t2, dir_path, dst_path, isdir=False)
    if not res:
        logger.error(f'Upload failed with the path: {dst_path}')
    logger.info(f'PLATFORM:Balance | LOCAL_PATH:{dir_path} | DST_PATH:{dst_path}')
    return res

