"""
middle proxy server  ---- author: zwb
client:
    py拉selenium
        监听所有请求
            转发至中转服务器
server:
    tornado 等待请求
        :param request(url, headers)
            重构headers(UA,COOKIE)
            发送异步的url

"""
import tornado
import tornado.ioloop
import tornado.web
import tornado.httpclient


class Monitor(tornado.web.RequestHandler):

    async def get(self):
        print(self.request.uri)
        url = f'https:/{self.request.uri}'
        print(url)
        print(self.request.connection)
        # self.request.headers['Host'] = 'appgrowing.cn'
        print(self.request.headers)
        c = tornado.httpclient.AsyncHTTPClient()
        url = 'http://www.taobao.com'
        r = tornado.httpclient.HTTPRequest(url, follow_redirects=True)
        resp = await c.fetch(r)
        self.write(resp.body)

    def post(self):
        ...


def run():
    return tornado.web.Application([
        (r"/.*?appgrowing.*?", Monitor),

    ], debug=True)


if __name__ == "__main__":
    app = run()
    app.listen(8888)
    print('server is running...')
    tornado.ioloop.IOLoop.current().start()


