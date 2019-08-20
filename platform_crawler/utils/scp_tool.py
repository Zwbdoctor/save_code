# from pexpect import spawn, EOF
import paramiko
import pexpect
import scp
import os
import logging
from time import strftime

from platform_crawler.settings import BASEDIR, GlobalVal


logger = None


class TransferWithExpect:

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        print('Transfer working...')

    def transfer(self, dst_path, source_files, is_dir=False):
        passwd_key = '.*asword.*'
        if is_dir:
            cmd_line = 'scp -r %s %s@%s:%s' % (source_files, self.user, self.ip, dst_path)
        else:
            cmd_line = 'scp %s %s@%s:%s' % (source_files, self.user, self.ip, dst_path)
        try:
            child = pexpect.spawn(cmd_line)
            child.expect(passwd_key)
            child.sendline(self.passwd)
            child.expect(pexpect.EOF)
            print('Transfer work finished!')
        except Exception as e:
            print('upload failed')
            print(e)

     
class RemoteShellWithExpectScript:

    def __init__(self, host=None, user=None, pwd=None):
        self.host = '139.224.116.116' if not host else host
        self.user = 'root' if not user else user
        self.pwd = 'hhmt@pwd@123' if not pwd else pwd

    def deal_path(self, path):
        path = path.replace('\\', '/').split(':')
        path = '/cygdrive/%s%s' % (path[0].lower(), path[1])
        return path

    def put(self, local_path, remote_path, send=True, isdir=1):
        mth = 'exp_scp_send' if send else 'exp_scp_get'
        shell_path = os.path.join(BASEDIR, 'utils', mth)
        # shell_path = self.deal_path(shell_path)
        # local_path = self.deal_path(local_path)
        param_dict = {
            'shell_path': shell_path, 'host': self.host, 'port': '22', 'user': self.user, 'passwd': self.pwd,
            'src_file': local_path, 'dst_file': remote_path, 'isdir': isdir
        }
        cmd = "expect %(shell_path)s %(host)s %(port)s %(user)s %(passwd)s %(src_file)s %(dst_file)s %(isdir)s" % param_dict
        res = os.system(cmd)
        if res != 0:
            return False
        return True


class RemoteShell:

    def __init__(self, host='139.224.116.116', port=22, user='root', pwd='hhmt@pwd@123'):
        self.host = host
        self.port = port
        self.username = user
        self.pwd = pwd

    @property
    def __transport(self):
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.pwd)
        return transport

    def close(self):
        self.__transport.close()

    def run_cmd(self, command):
        """
         执行shell命令,返回字典
         return {'color': 'red','res':error}或
         return {'color': 'green', 'res':res}
        :param command:
        :return:
        """
        ssh = paramiko.SSHClient()
        ssh._transport = self.__transport
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command)
        # 获取命令结果
        res = self.to_str(stdout.read())
        # 获取错误信息
        error = self.to_str(stderr.read())
        # 如果有错误信息，返回error
        # 否则返回res
        if error.strip():
            return {'color': 'red', 'res': error}
        else:
            return {'color': 'green', 'res': res}

    def upload(self, local_path, target_path, isdir=False):
        # 连接，上传
        # sftp = paramiko.SFTPClient.from_transport(self.__transport)
        try:
            with scp.SCPClient(self.__transport) as sftp:
                # 将location.py 上传至服务器 /tmp/test.py
                sftp.put(local_path, target_path, recursive=isdir)
                # print(os.stat(local_path).st_mode)
                # 增加权限
                # sftp.chmod(target_path, os.stat(local_path).st_mode)
                # sftp.chmod(target_path, 0o755)  # 注意这里的权限是八进制的，八进制需要使用0o作为前缀
            return True
        except:
            return False

    def download(self, target_path, local_path):
        # 连接，下载
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # 将location.py 下载至服务器 /tmp/test.py
        sftp.get(target_path, local_path)

    def to_str(self, bytes_or_str):
        """
        把byte类型转换为str
        :param bytes_or_str:
        :return:
        """
        if isinstance(bytes_or_str, bytes):
            value = bytes_or_str.decode('utf-8')
        else:
            value = bytes_or_str
        return value

    # 销毁
    def __del__(self):
        self.close()


def init_dst_dir(platform, isCpa=False):
    global logger
    logger = logging.getLogger(GlobalVal.CUR_MAIN_LOG_NAME)
    cudate = strftime('%Y-%m-%d')
    if not isCpa:
        dst_path = '/data/python/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    else:
        dst_path = '/data/python/CPA/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    t = RemoteShell()
    test_host = '47.100.120.114'
    t2 = RemoteShell(host=test_host)
    if not t2.upload(os.path.join(BASEDIR, 'init_dir'), dst_path, isdir=True):
        logger.error("init dst dir failed with test env")
    if not t.upload(os.path.join(BASEDIR, 'init_dir'), dst_path, isdir=True):
        logger.error("init dst dir failed with real env")
    del(t, t2)
    logger.info(f'PLATFORM:{platform} | LOCAL_PATH:./init_dir | DST_PATH:{dst_path}')
    return {'succ': True}


def put(t1, t2, dir_path, dst_path):
    res1 = t1.upload(dir_path, dst_path, isdir=True)
    res2 = t2.upload(dir_path, dst_path, isdir=True)
    del(t1, t2)
    return True if res1 and res2 else False


def upload_file(dir_path, platform, isCpa=False):
    cudate = strftime('%Y-%m-%d')
    if not isCpa:
        dst_path = '/data/python/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    else:
        dst_path = '/data/python/CPA/%(platform)s/%(currentDay)s/' % {'platform': platform, 'currentDay': cudate}
    files = os.listdir(dir_path)
    if not files:
        # with open(os.path.join(dir_path, 'no_data.json'), 'w') as f:
        #     f.write('{"msg": "no data"}')
        return True
    t = RemoteShell()
    t2 = RemoteShell(host='47.100.120.11')          # test env
    res = put(t, t2, dir_path, dst_path)
    if not res:
        logger.error(f'Upload failed with the path: {dst_path}')
    logger.info(f'PLATFORM:{platform} | LOCAL_PATH:{dir_path} | DST_PATH:{dst_path}')
    return res


if __name__ == '__main__':
    r = RemoteShell('47.100.120.114')
    dst = '/data/python/tst/'
    source = os.path.join(os.path.abspath('../save_data'), )
    src = r'G:\python_work\python\commen\platform_crawler\save_data\Alios\2019-07-03\1248_2019-07-03_14-55-23_wangdi@btomorrow.cn'
    # r.put(source, dst)
    upload_file(src, 'Alios')
    # info = logger.info('DST_PATH | sdfsf}')



