import requests
from requests.adapters import HTTPAdapter


def get(url, params=None, headers=None, proxies=None, verify=True, timeout=60):
    s = requests.session()
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    ret = {'is_success': True}
    if params:
        s.params = params
    if headers:
        s.headers = headers
    if proxies:
        s.proxies = proxies
    if not verify:
        from urllib3 import disable_warnings, exceptions
        disable_warnings(exceptions.InsecureRequestWarning)
        s.verify = verify
    if timeout != 60:
        s.timeout = timeout
    try:
        ret['msg'] = s.get(url)
    except Exception as e:
        ret['msg'] = e
        ret['is_success'] = False
    finally:
        s.close()
        return ret


def post(url, data, params=None, headers=None, proxies=None, verify=True, timeout=60, json=None):
    s = requests.session()
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    ret = {'is_success': True}
    if params:
        s.params = params
    if json:
        s.json = json
    if headers:
        s.headers = headers
    if proxies:
        s.proxies = proxies
    if not verify:
        from urllib3 import disable_warnings, exceptions
        disable_warnings(exceptions.InsecureRequestWarning)
    s.verify = verify
    if timeout != 20:
        s.timeout = timeout
    try:
        ret['msg'] = s.post(url, data=data)
    except Exception as e:
        ret['msg'] = e
        ret['is_success'] = False
    finally:
        s.close()
        return ret
