import logging
import json
from platform_crawler.utils.post_get import post
from platform_crawler import settings

post_res_url = 'http://erp.btomorrow.cn/adminjson/ERP_ReportPythonCrawlerTask'


def post_res(task_id, account, platform, file_path, status, has_data=1, has_pic=1):
    """
    上报结果
    :param task_id:
    :param account:
    :param platform: 任务类型
    :param file_path: 上传目录的服务器相对路径
    :param status: booltype, 是否成功
    :param has_data: int, 是否有数据
    :param has_pic: int, 是否有截图
    :return: 返回是否上报成功
    """
    logger = logging.getLogger('%s.post_res' % settings.GlobalVal.CUR_MAIN_LOG_NAME)
    post_data = {'taskId': task_id, 'errorCode': None, 'status': None, 'statusDesc': None, 'account': account,
                 'platform': platform, 'filePathCatalog': '', 'flag': settings.GlobalVal.CUR_TASK_TYPE, 'isScreenshots': has_pic,
                 'isData': has_data}
    dst_file_path = file_path if file_path else settings.GlobalVal.DST_DIR
    if status and status == 5:
        need_change = {'status': 5, 'statusDesc': '爬虫逻辑错误', 'filePathCatalog': dst_file_path}
    elif status:
        need_change = {'status': 3, 'statusDesc': '成功'}
    else:
        need_change = {'status': 4, 'statusDesc': '账号无效', 'errorCode': 10000, 'filePathCatalog': dst_file_path,
                       'isData': 0, 'isScreenshots': 0}
        # need_change = {'status': 5, 'statusDesc': '账号无效'}
    post_data.update(need_change)

    logger.info('Post Data: %s' % post_data)

    data = json.dumps(post_data)
    res = post(post_res_url, data=data, headers={'Content-Type': 'application/json'})
    if not res['is_success']:
        logger.warning('上报失败')
        logger.error(res.get('msg'), exc_info=1)
        # 上报失败
        return False
    else:
        # 上报成功
        logger.info('Post success! ret_msg: %s' % res['msg'].content.decode('utf-8'))
        return True
