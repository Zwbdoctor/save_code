import os
import sqlite3
from win32.win32crypt import CryptUnprotectData

cookiepath = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Cookies"


def get_cks(sql):
    cks = []
    with sqlite3.connect(cookiepath) as conn:
        cu = conn.cursor()
        cookies = cu.execute(sql).fetchall()
        for host_key, name, encrypted_value in cookies:
            ck = {}
            ck['domain'] = host_key
            ck['name'] = name
            try:
                ck['value'] = CryptUnprotectData(encrypted_value)[1].decode()
            except:
                ck['value'] = encrypted_value
            cks.append(ck)
    return cks


def getcookiefromchrome(host=None):
    sql = "select host_key,name,encrypted_value from cookies where host_key='%s'"
    ck = {}
    if isinstance(host, list):
        for h in host:
            ck[h] = get_cks(sql % h)
    else:
        ck[host] = get_cks(sql % host)
    return ck


def delete_cookie(host):
    sql = "delete from cookies where host_key='%s'" % host
    with sqlite3.connect(cookiepath) as conn:
        cu = conn.cursor()
        cu.execute(sql)
        conn.commit()


def delete_all_cookies(hosts):
    if isinstance(hosts, list):
        for h in hosts:
            delete_cookie(h)
    else:
        delete_cookie(hosts)


hosts = [
    '.taobao.com', 'g.alicdn.com', '.mmstat.com', 'login.taobao.com', '.login.taobao.com',
]
res = getcookiefromchrome(host=hosts)
print(res)
# delete_all_cookies(hosts)


