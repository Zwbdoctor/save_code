import socket
import urlparse
import select
import threading

BUFLEN = 8192


class Proxy(object):
    def __init__(self, conn, addr):
        self.source = conn
        self.request = ""
        self.headers = {}
        self.destnation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.run()

    def receive(self, sock, n, timeout=20):
        (rlist, wlist, elist) = select.select([sock], [], [], timeout)
        if sock in rlist:
            return sock.recv(n)
        else:
            raise(RuntimeError, "timed out on %r" % (sock,))

    def stream_examine(self, proto, addr):
        s = socket.socket(proto, socket.SOCK_STREAM)
        s.connect(addr)
        s.sendall()
        buf = data = self.receive(s, BUFLEN)
        while data and '\n' not in buf:
            data = self.receive(s, 100)
            buf += data
        s.close()

    def get_headers(self):
        header = ''
        while True:
            header += self.source.recv(BUFLEN)
            index = header.find('\n')
            if index > 0:
                break
        firstLine = header[:index]
        self.request = header[index + 1:]
        self.headers['method'], self.headers['path'], self.headers['protocol'] = firstLine.split()

    def conn_destnation(self):
        url = urlparse.urlparse(self.headers['path'])
        hostname = url[1]
        port = "80"
        if hostname.find(':') > 0:
            addr, port = hostname.split(':')
        else:
            addr = hostname
        port = int(port)
        ip = socket.gethostbyname(addr)
        # print ip,port
        self.destnation.connect((ip, port))
        data = "%s %s %s\r\n" % (self.headers['method'], self.headers['path'], self.headers['protocol'])
        self.destnation.send(data + self.request)
        print
        data + "\n" + self.request

    def renderto(self):
        readsocket = [self.destnation]
        while True:
            data = ''
            (rlist, wlist, elist) = select.select(readsocket, [], [], 3)
            if rlist:
                data = rlist[0].recv(BUFLEN)
                if len(data) > 0:
                    self.source.send(data)
                else:
                    break

    def run(self):
        self.get_headers()
        self.conn_destnation()
        self.renderto()


class Server(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.server.bind((host, port))
        self.server.listen(5)

    def start(self):
        while True:
            try:
                conn, addr = self.server.accept()
                Proxy(conn, addr)

            except:
                conn.close()


def test():
    s = Server('127.0.0.1', 8888)
    threads = []
    for i in range(40):
        t = threading.Thread(target=s.start, args=())
        t.daemon = True  # In case this function raises.
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    test()
