import os
imgs_path = os.path.join(os.path.abspath('./imgs'), 'huawei_imgs')
log_path = os.path.join(os.path.abspath('./logs'), 'huawei')
# js_path = os.path.join(os.path.abspath('./utils'), 'preload.js')


img_dicts = [
    {'img_name': 'user_name', 'img_path': imgs_path + r'\username.png', 'sleep_time': 1, 'location': None,
     'input_data': 'chenkx@ishugui.com', 'need_current': False},
    {'img_name': 'passwd', 'img_path': imgs_path + r'\passwd.png', 'sleep_time': 2, 'location': None,
     'input_data': 'dzkj2016', 'need_current': False},
    {'img_name': 'click_to_vc', 'img_path': imgs_path + r'\click_vc.png', 'sleep_time': 2, 'location': None,
     'input_data': None, 'need_current': False},
]

url = 'https://hwid1.vmall.com/CAS/portal/loginAuth.html?validated=true&themeName=red&service=https%3A%2F%2Flogin1.' \
      'vmall.com%2Foauth2%2Fv2%2Flogin%3Fclient_id%3D100101457%26display%3Dpage%26h%3D1533709949.2438%26lang%3Dzh-c' \
      'n%26redirect_uri%3Dhttps%253A%252F%252Fdeveloper.huawei.com%252Fconsumer%252Fcn%252Fservice%252Fapcs%252Fapp' \
      '%252FhandleLogin.html%26response_type%3Dcode%26state%3D33599682%26v%3D5a1b82fb4bd77392720c73e41deed42d55b748' \
      'f944714005042a602119dfb7fa&loginChannel=4000200&reqClientType=2058&lang=zh-cn'

page_dict = {'url': url, 'pst': 3,
             'log_path': log_path, 'log_file': 'huawei.log',
             # 'start_point': '824,381',
             'ret_data': {'startDate': None, 'account': "jiabao@btomorrow.cn", 'cookie': None, 'errorCode': 0,
                          'platform': 'huawei', 'errMsg': '成功'},
             'passwd': 'Hhmt123456',
             'host': '.developer.huawei.com',
             'delete_host_cookie': ['hwid1.vmall.com', '.hwid1.vmall.com'],
             'opera_type': 'sys',
             'login': imgs_path + r'\login.png',
             'vc_path': imgs_path + r'\do_verify.png',
             'copy_url': imgs_path + r'\copy_url.png',
             }
