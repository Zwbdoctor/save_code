"""抽离出的结果处理器"""
import logging


def result_handler(task_func, um, log_name, post_res, **kwargs):
    logger = logging.getLogger(log_name)
    try:
        res = task_func(um)
        result_kwargs = res.get('result_kwargs')
        if not result_kwargs:
            result_kwargs = {'has_data': 0, 'has_pic': 0}
        # 上报服务器
        if res.get('succ'):
            # 成功
            if not post_res(um['id'], um['account'], um['platform'], res.get('data_path'), status=True, **result_kwargs):
                logger.error('----------after upload files, post result failed !!!!')
                return False
            else:
                logger.info('Upload success! Post result success!')
                return True
        elif not res.get('succ') and res.get('invalid_account'):
            return True
        else:
            logger.warning('爬虫逻辑错误，所有可能信息如下：')
            logger.error(res)
            if not post_res(um['id'], um['account'], um['platform'], None, status=5):
                logger.error('---------- post error message failed !!!!')
            return False
            # logger.smtp('发送邮件')
    except Exception as e:
        logger.warning('Got an err about account %s, detail msg like this:' % um['account'])
        logger.error(e, exc_info=1)
        post_res(um['id'], um['account'], um['platform'], None, status=5)
        return False
