import requests
import logging
import json
from requests.utils import quote
from re import search

logger = None


class BaseCrawler:

    def __init__(self, headers=None, proxies=None, spider=None):
        global logger
        self.ret = {'succ': True}
        self.s = None
        self.headers = headers
        self.proxies = proxies
        logger = logging.getLogger(spider)

    def execute(self, method, url, session=False, data=None, params=None, verify=False, timeout=60, json_ojb=None, content_type=None, referer=None, print_payload=True):
        logger.info('innerUrl ------- %s: %s' % (method, url))
        if content_type:
            self.headers['Content-type'] = content_type
        if session:
            self.s = session
        else:
            self.s = requests.session()
            self.s.headers = self.headers
            if verify:
                self.s.verify = verify
            if json_ojb:
                self.s.json = json_ojb
        if params:
            self.s.params = params
            logger.info('params: %s' % json.dumps(params))
        if timeout != 60:
            self.s.timeout = timeout
        if self.proxies:
            self.s.proxies = self.proxies
        try:
            if method == 'GET':
                if self.headers.get('Content-type'):
                    self.headers.pop('Content-type')
                self.ret['msg'] = self.s.get(url)
            elif method == 'POST':
                if print_payload:
                    logger.info('payload: %s' % json.dumps(data))
                self.ret['msg'] = self.s.post(url, data)
        except Exception as e:
            self.ret['msg'] = e
            self.ret['succ'] = False
        finally:
            if not session:
                self.s.close()
            ref = '%s?%s' % (url, '&'.join(['%s=%s' % (k, quote(v)) for k, v in params.items()])) if params else url
            self.headers['Referer'] = ref if not referer else referer
            if self.ret.get('succ'):
                try:
                    self.set_cookie()
                except AttributeError:
                    pass
                except Exception as es:
                    logger.warning(es)
            return self.ret

    def set_cookie(self):
        cookies = self.ret.get('msg').cookies.items()
        cookie_dict = {v.split('=')[0]: v.split('=')[1] for v in self.headers.get('Cookie').split('; ')}
        cookie_dict.update({k: v for k, v in cookies})
        self.headers['Cookie'] = '; '.join(['%s=%s' % (k, v) for k, v in cookie_dict.items()])

    def deal_result(self, result_content, json=False, err_type=None):
        """处理请求结果"""
        if result_content.get('succ') and search(r'parent.parent.topFrame.logoffFlag=1', result_content.get('msg').text):
            # 处理login lost
            logger.info('%s login lost' % err_type)
            logger.critical('%s login lost' % err_type)
            return {'succ': False, 'msg': 'Login Lost!!', 'data': result_content.get('msg').text}
        elif result_content.get('succ') and search(r"/ebankc/newperbank/sessionerror.jsp", result_content.get('msg').text):
            # 处理login lost
            logger.info('%s login lost' % err_type)
            logger.critical('%s login lost' % err_type)
            return {'succ': False, 'msg': 'Login Lost!!', 'data': result_content.get('msg').text}
        elif not result_content.get('succ'):
            logger.error(result_content.get('msg'), exc_info=1)
            return {'succ': False, 'msg': result_content, 'data': result_content.get('msg').text}
        elif result_content.get('msg').status_code not in [200, 304]:
            logger.error(result_content.status_code)
            logger.error(result_content.content.decode('utf-8'))
            return {'succ': False, 'msg': result_content, 'data': result_content.get('msg').text}
        if json:
            result_content.update({'msg': result_content.get('msg').json()})
        result_content.update({'msg': result_content.get('msg').text})
        return result_content


# if __name__ == '__main__':
#     headers = {
#         'accept': "application/json, text/javascript",
#         'content-type': "application/x-www-form-urlencoded",
#         'cookie': "cna=CKwPFBb6HhUCAXFXek3ktBZe; c_cf=76966e4b-82d4-427b-a478-f7d36b494af7; login_yunosid=01%E8%BE%89%E7%85%8C%E6%98%8E%E5%A4%A9; login_yunos_ticket=5742314e8b34612a1c5c038fe282f3a308d65279fec8efbd8628c081f06ed685; session_id=1539834779271kboICz1pMaG; isg=BIuL30ZFVJoriojCvDtHVb4NGi-1iJwn9x7MjP2JYEohHKt-hfI78-q98lxXPPea",
#         'referer': "https://e.yunos.com/",
#         'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
#     }
#     c = BaseCrawler(headers=headers)
#     params = {"page_size":"15","page":"1","keyword":"","rpt_start_time":"2018-10-18","rpt_end_time":"2018-10-18","sort_by":"7","sort_desc":"1"}
#     # url = 'https://e.yunos.com/api/campaign/list'
#     url = 'https://e.yunos.com/api/campaign/list'
#     res = c.execute('GET', url, params=params)
#     resp = res.get('msg').json()
#     url2 = 'https://e.yunos.com/api/member/balance'
#     res2 = c.execute('GET', url, session=res.get('session')).get('msg').json()
#     print(res2)
