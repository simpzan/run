#!/usr/bin/env python3
from run import sh, sh_out, log, run_main
import os

def tugua():
    cmd = '''
        curl -s 'https://www.dapenti.com/blog/index.asp' \
            -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' \
        | iconv -f GBK -t UTF-8 \
        | grep -E "【喷嚏图卦" \
        | head -n1
    '''
    ret = sh_out(cmd)
    # print(ret)
    import re
    match = re.search(r"""<a\s+[^>]*href=([^\s>]+)[^>]*\stitle=['"]([^'"]+)['"]""", ret)
    if not match: return
    href, title = match.groups()
    url = f'https://www.dapenti.com/blog/{href}'
    return url, title

def test():
    url, title = tugua()
    print(url, title)
    title, body = title.split('】')
    title = title[1:]
    print(title, body)
    notify(title, body, 'penti_tugua', url)

def bark(key, title, body, group='', url=''):
    """Send notification via Bark (https://api.day.app/)"""
    import urllib.parse
    import urllib.request
    data = urllib.parse.urlencode({'title': title, 'body': body, 'group': group, 'url': url}).encode('utf-8')
    url = f'https://api.day.app/{key}'
    req = urllib.request.Request(url, data=data, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except Exception as e:
        log.e(f"bark error: {e}")
        return False
def notify(title, body, group='', url=''):
    key = os.getenv('BARK_KEY')
    if not key: return log.e('BARK_KEY is not set')
    bark(key, title, body, group, url)
def notify_test():
    notify('喷嚏图卦20260427', '人类终于突破了两小时这个天堑', 'penti_tugua')


def hello():
    log.i('kernel info')
    sh("uname -a")
if __name__ == "__main__": run_main(__file__)
