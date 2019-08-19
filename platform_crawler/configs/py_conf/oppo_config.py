import os
imgs_path = os.path.join(os.path.abspath('.'), 'imgs\\oppo_imgs\\')
log_path = os.path.join(os.path.abspath('./logs'), 'oppo')
# js_path = os.path.join(os.path.abspath('./utils'), 'preload.js')


# img_dicts = [
#     {'img_name': 'user_name', 'img_path': imgs_path + r'\user_name.png', 'sleep_time': 1, 'location': None,
#      'input_data': 'wangdi@btomorrow.cn', 'need_current': False},
# ]
page_dict = {'url': 'https://e.oppomobile.com/login_token', 'log_path': log_path, 'pst': 3,
             'log_file': 'oppo.log', 'img_path': imgs_path + 'vc.png',
             'ret_data': {'startDate': None, 'account': "他趣1", 'cookie': None, 'errorCode': 0, 'platform': 'oppo',
                          'errMsg': '成功'},
             'passwd': 'tq1234'}
