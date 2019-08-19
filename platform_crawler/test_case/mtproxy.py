from mitmproxy import http


def response(flow: http.HTTPFlow):
    print(flow.request.pretty_url)
    # if flow.request.url.startswith('https://g.alicdn.com/secdev/sufei_data'):
    if 'secdev/sufei_data' in flow.request.pretty_url:
        print(' ----------------  url matched alicdn')
        flow.response.content = flow.response.content.replace(b'$cdc_asdjflasutopfhvcZLmcfl_', b'randomBla')

