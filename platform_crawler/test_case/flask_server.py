from flask import Flask, Response

app = Flask(__name__)


@app.route('/resend/api', methods=['GET'])
def mids():
    resp = Response()
    resp.set_cookie('AG_Token', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2MiOjIxNDc3MCwiaWQiOiI4MzZkMDE1My0xZjE1LTNkYjYtYmUxNy04MWI2ZDhkNmJlOTIiLCJleHAiOjE1NjMwMDg5NzUsImlhdCI6MTU2MDQxNjk3Nn0.1s3DC3FsyXJku_mw8D-81gZCzsPTA7X5czQwxLfqSXo')
    resp.set_cookie('AG_Userid', '836d0153-1f15-3db6-be17-81b6d8d6be92', domain='.appgrowing.cn')
    resp.response = '<h1>who ou</h1>'
    return resp


if __name__ == '__main__':
    app.run(port=8080, debug=True)

