import paramiko
import pexpect
import scp
import os

from platform_crawler.settings import BASEDIR


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

     
class UploadWithExpectScript:

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
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        try:
            with scp.SCPClient(self.__transport) as scp_client:
                print('正在上传...')
                scp_client.put(local_path, target_path, recursive=isdir)
                sftp.chmod(target_path, 0o755)
                print('上传完毕!')
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            sftp.close()
            self.__transport.close()

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


if __name__ == '__main__':
    # r = RemoteShell(host='115.231.130.17', port=20277, user='root', pwd='abcd1234')
    r = RemoteShell()
    dst = '/data/python/balance_data'
    source = os.path.join(os.path.abspath('../save_data'), 'balance_data')
    src = r'deploy.tar.gz'
    # r.put(source, dst)
    r.upload(source, dst, isdir=True)
    # info = logger.info('DST_PATH | sdfsf}')



