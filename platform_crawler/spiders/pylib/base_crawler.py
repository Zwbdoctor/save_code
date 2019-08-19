import requests
import logging

import urllib3
from requests.utils import quote
from requests.adapters import HTTPAdapter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)     # ignore the IR Warning

logger = None


class BaseCrawler:

    def __init__(self, headers=None, proxies=None, spider=None):
        global logger
        self._ret = {'succ': True}
        self.__s = None
        self._headers = headers
        self._proxies = proxies
        self.last_url = None
        logger = logging.getLogger('%s.base_crawler' % spider)

    def execute(self, method, url, session=False, data=None, params=None, headers=None, verify=True, timeout=60,
                json_ojb=None, content_type=None, referer=None, print_payload=True, set_cookies=False):
        logger.debug('innerUrl ------- %s: %s' % (method, url))
        if headers:
            self._headers = headers
        if content_type:
            self._headers['Content-Type'] = content_type
        if session:
            self.__s = session
        else:
            self.__s = requests.session()
            self.__s.mount('http://', HTTPAdapter(max_retries=2))       # Retries after time out
            self.__s.mount('https://', HTTPAdapter(max_retries=2))
            self.__s.headers = self._headers
            if json_ojb:
                self.__s.json = json_ojb
        if params:
            self.__s.params = params
            logger.debug('params: %s' % params)
        if self._proxies:
            self.__s.proxies = self._proxies
        self.__s.verify = verify
        self.__s.timeout = timeout if timeout != 120 else 120
        header_keys = self._headers.keys()
        try:
            if method == 'GET':
                if 'Content-Type' in header_keys or 'content-type' in header_keys:
                    self._headers.pop('Content-Type')
                self._ret['msg'] = self.__s.get(url)
            elif method == 'POST':
                if print_payload:
                    logger.debug('payload: %s' % data)
                self._ret['msg'] = self.__s.post(url, data)
        except Exception as e:
            self._ret['msg'] = e
            self._ret['succ'] = False
        finally:
            if not session:
                self.__s.close()
            # set referer
            if params and not self.last_url:
                ref = '%s?%s' % (url, '&'.join(['%s=%s' % (k, quote(str(v))) for k, v in params.items()]))
            elif params and self.last_url:
                ref = '%s?%s' % (self.last_url, '&'.join(['%s=%s' % (k, quote(str(v))) for k, v in params.items()]))
            elif not params and self.last_url:
                ref = self.last_url
            else:
                ref = url
            self.last_url = url
            ref_key = 'Referer' if 'Referer' in header_keys else 'referer'
            self._headers[ref_key] = ref if not referer else referer
            if self._ret.get('succ'):
                try:
                    if set_cookies:
                        self.__set_cookie()
                    else:
                        pass
                except AttributeError:
                    pass
                except Exception as es:
                    logger.warning(es)
            return self._ret

    def __set_cookie(self):
        cookies = self._ret.get('msg').cookies.items()
        cookie_dict = {v.split('=')[0]: v.split('=')[1] for v in self._headers.get('Cookie').split('; ')} if self._headers.get('Cookie') else {}
        cookie_dict.update({k: v for k, v in cookies})
        self._headers['Cookie'] = '; '.join(['%s=%s' % (k, v) for k, v in cookie_dict.items()])

    def base_result(self, json_str=False, get_cookie=False, file=False, encoding=None):
        if not self._ret.get('succ'):  # 网络错误
            logger.error(self._ret.get('msg'), exc_info=self._ret.get('msg'))
            self._ret.update({'succ': False, 'msg': self._ret.get('msg')})
            return self._ret
        elif self._ret.get('msg').status_code not in [200, 304]:
            logger.error(self._ret.get('msg').status_code)
            logger.error(self._ret.get('msg').text)
            self._ret.update({'succ': False, 'msg': self._ret.get('msg').text, 'data': self._ret.get('msg')})
            return self._ret
        elif self._ret.get('succ'):
            if not json_str:
                if not file:
                    try:
                        msg = self._ret.get('msg').text
                    except:
                        msg = self._ret.get('msg').content.decode('utf-8')
                    if encoding:
                        msg = self._ret.get('msg').content.decode(encoding)
                else:
                    msg = self._ret.get('msg').content
                self._ret.update({'msg': msg})
            else:
                try:
                    self._ret.update({'msg': self._ret.get('msg').json()})
                except:
                    self._ret.update({'succ': False, 'msg': self._ret.get('msg').text})
            if get_cookie:
                self._ret.update({'cookie': self._headers.get('Cookie')})
            return self._ret

    def deal_result(self, result, **kwargs):
        """
        处理请求结果
        Args:
            result: http result
            kwargs: json_str->False, get_cookie->False, file->False, encoding-> None
        """
        return self.base_result(**kwargs)

