import paramiko  # 用于调用scp命令
import os
from scp import SCPClient


# 将指定目录的图片文件上传到服务器指定目录
# remote_path远程服务器目录
# file_path本地文件夹路径
# img_name是file_path本地文件夹路径下面的文件名称
class ScpTools:

    def __init__(self, host, port=22, username='root', password=None):
        self.host = host
        self.port = port
        self.user = username
        self.password = password

    def upload_img(self, remote_path=None, local_path=None):
        with paramiko.SSHClient() as ssh_client:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            ssh_client.connect(self.host, self.port, self.user, self.password)
            scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
            print(f'local_path: {local_path}')
            try:
                scpclient.put(local_path, remote_path)
            except FileNotFoundError as e:
                print(e)
                print("系统找不到指定文件" + local_path)
            else:
                print("文件上传成功")


if __name__ == "__main__":
    st = ScpTools('47.100.245.190', username='root', password='hhmt@pwd@123')
    st.upload_img(os.path.abspath('../node_md'), '/data/python/tst/node_md')


