# from jpype import *
import os
import logging
import requests
import json
# from chardet import detect


logger = logging.getLogger('run_java')


def post_data(data, statusinfo, username):
    # post data and status
    data['username'] = username
    print(data)
    json_data = {
        'json_str': data,
        'result_status': statusinfo.split(':')[1]
    }
    session = requests.session()
    url = 'http://erp.btomorrow.cn/adminjson/ERP_SaveCrawlerStatus'
    try:
        resp = session.post(url, data=json.dumps(json_data), timeout=10).content
        resp = json.loads(resp.decode('utf-8'))
        logger.info(resp)
        if resp['errorCode'] != 0:
            logger.info('结果上报失败: %s\n%s' % (json.dumps(data), statusinfo))
        logger.info('上报成功： %s' % (json_data))
    finally:
        session.close()

def run_perl(json_data):
    logger.info('Begin:' + json.dumps(json_data))
    username = json_data.pop('username')

    jarpath = os.path.join(os.path.abspath('.'), 'lib\\')
    dirs = os.listdir(jarpath)
    lib_path = ';'.join([jarpath + e for e in dirs])

    json_str = json.dumps(json_data).replace('"', "'")
    cmd = 'java -cp ' + lib_path + ' com.hh.erp.crawler.main.CrawlerMain ' +  '"' + json_str +  '"'
    logger.info('CMD:' + 'java -cp libfiles... com.hh.erp.crawler.main.CrawlerMain ' + '"' + json_str + '"')
    data = os.popen(cmd).read()
    logger.info('RET:' + data)

    res = data.split('\n')[::-1]
    statusinfo = ''

    # import pdb
    # pdb.set_trace()

    for e in res:
        if not e:
            continue
        #e = e.decode(detect(e)['encoding'])#.encode('utf-8')
        if e.startswith('status'):
            statusinfo = e
            break
    logger.info('statusinfo:' + statusinfo.split(':')[1])
    # 上报结果
    post_data(json_data, statusinfo, username)
	
    if not statusinfo:
        logger.info('statusinfo is empty')
        return False
		
    if not statusinfo.split(':')[1].startswith('0'):
        logger.info('run error')
        return False
    logger.info('run success')
    return True

