import os
imgs_path = os.path.join(os.path.abspath('./imgs'), 'vivo_imgs')
log_path = os.path.join(os.path.abspath('./logs'), 'vivo')
# js_path = os.path.join(os.path.abspath('./utils'), 'preload.js')


img_dicts = [
    {'img_name': 'user_name', 'img_path': imgs_path + r'\username.png', 'sleep_time': 1, 'location': None,
     'input_data': 'chenkx@ishugui.com', 'need_current': False},
    {'img_name': 'passwd', 'img_path': imgs_path + r'\passwd.png', 'sleep_time': 2, 'location': None,
     'input_data': 'dzkj2016', 'need_current': False},
    {'img_name': 'click_to_vc', 'img_path': imgs_path + r'\click_vc.png', 'sleep_time': 2, 'location': None,
     'input_data': None, 'need_current': False},
]


page_dict = {'url': 'http://id.vivo.com.cn', 'pst': 3,
             'log_path': log_path, 'log_file': 'vivo.log',
             'start_point': '824,381',
             'ret_data': {'startDate': None, 'account': "chenkx@ishugui.com", 'cookie': None, 'errorCode': 0,
                          'platform': 'vivo', 'errMsg': '成功'},
             'passwd': 'dzkj2016',
             'host': ['dev.vivo.com.cn', '.vivo.com.cn'],
             'delete_host_cookie': ['dev.vivo.com.cn', '.vivo.com.cn'],
             'opera_type': 'sys',
             'login': imgs_path + r'\login.png',
             'vc_path': imgs_path + r'\do_verify.png',
             'copy_url': imgs_path + r'\copy_url.png',
             }
