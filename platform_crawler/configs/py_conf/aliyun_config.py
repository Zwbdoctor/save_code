import os
imgs_path = os.path.join(os.path.abspath('./imgs'), 'aliyun_imgs\\')
log_path = os.path.join(os.path.abspath('./logs'), 'aliyun')
# js_path = os.path.join(os.path.abspath('./utils'), 'preload.js')


img_dicts = {
    'user_name': imgs_path + 'user_name.png',
    'passwd': imgs_path + 'passwd.png',
    'btn_login': imgs_path + 'btn_login.png'
}

page_dict = {'url': 'http://e.yunos.com/', 'log_path': log_path, 'pst': 3, 'log_file': 'aliyun_cookie.log',
             'ret_data': {'type': 9, 'account': "wangdi@btomorrow.cn", 'cookie': None},
             'host': ['e.yunos.com', '.yunos.com'], 'opera_type': 'sys',
             'delete_host_cookie': [
                 'g.alicdn.com', '.mmstat.com', 'e.yunos.com', '.yunos.com'
             ]}
