import requests,time

url = 'http://ip:port/weibo/add/'

ss = []   #添加 账户密码 自动
n = 0
for i in ss:
    phont = i.split('----')
    href = url + phont[0] + '/' + phont[1]
    resp = requests.get(href)
    print(resp.text)
    print(n)
    n += 1
    time.sleep(1)