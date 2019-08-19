import requests


def uploads():
    url = 'http://144.34.194.228/upImg/3050/2x3fd'
    with open('check_old.png', 'br') as im:
        data = im.read()
    resp = requests.post(url, files={'image': ('2x3fd.png', data)})
    print(resp.text)


uploads()
