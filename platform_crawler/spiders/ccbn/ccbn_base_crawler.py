import requests
import logging
import json

import urllib3
from requests.utils import quote
from requests.adapters import HTTPAdapter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logger = None


class BaseCrawler:

    def __init__(self, headers=None, proxies=None, spider=None):
        global logger
        self.ret = {'succ': True}
        self.s = None
        self.headers = headers
        self.proxies = proxies
        self.last_url = None
        logger = logging.getLogger(spider)

    def execute(self, method, url, session=False, data=None, params=None, verify=False, timeout=60, json_obj=None, content_type=None, referer=None, print_payload=True):
        logger.info('innerUrl ------- %s: %s' % (method, url))
        if content_type:
            self.headers['Content-Type'] = content_type
        if session:
            self.s = session
        else:
            self.s = requests.session()
            self.s.mount('http://', HTTPAdapter(max_retries=2))       # Retries after time out
            self.s.mount('https://', HTTPAdapter(max_retries=2))
            self.s.headers = self.headers
            if json_obj:
                self.s.json = json_obj
        self.s.verify = verify
        if params:
            self.s.params = params
            logger.info('params: %s' % json.dumps(params))
        if timeout != 60:
            self.s.timeout = timeout
        if self.proxies:
            self.s.proxies = self.proxies
        try:
            if method == 'GET':
                if self.headers.get('Content-Type'):
                    self.headers.pop('Content-Type')
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
            if params and not self.last_url:
                ref = '%s?%s' % (url, '&'.join(['%s=%s' % (k, quote(v)) for k, v in params.items()]))
            elif params and self.last_url:
                ref = '%s?%s' % (self.last_url, '&'.join(['%s=%s' % (k, quote(v)) for k, v in params.items()]))
            elif not params and self.last_url:
                ref = self.last_url
            else:
                ref = url
            self.last_url = url
            logger.warning(ref)
            self.headers['Referer'] = ref if not referer else referer
            if self.ret.get('succ'):
                try:
                    # self.set_cookie()
                    pass
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

    def base_result(self, json_str=False):
        if not self.ret.get('succ'):        # 网络错误
            logger.error(self.ret.get('msg'), exc_info=self.ret.get('msg'))
            self.ret.update({'succ': False, 'msg': self.ret.get('msg')})
            return
        elif self.ret.get('msg').status_code not in [200, 304]:
            logger.error(self.ret.get('msg').status_code)
            logger.error(self.ret.get('msg').text)
            self.ret.update({'succ': False, 'msg': self.ret.get('msg').text, 'data': self.ret.get('msg')})
            return
        elif json_str and self.ret.get('succ'):
            self.ret.update({'msg': self.ret.get('msg').json()})
        else:
            self.ret.update({'msg': self.ret.get('msg').text})

    def deal_result(self, result, json_str=False, err_type=None):
        """处理请求结果"""
        pass


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
