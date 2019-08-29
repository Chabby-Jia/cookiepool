





import requests

PROXY_POOL_URL = 'http://ip:port/random'
S = requests.session()
S.keep_alive = False



def get_proxy():
    """
    通用获取随机代理
    格式： 0.0.0.0：0000
    :return:
    """
    #限制条件，增加判断
    ret = False
    try:
        response = S.get(PROXY_POOL_URL)
        if response.status_code == 200:
            ret = True
            S.close()
            return response.text
    except ConnectionError as e:
        print('获取代理失败...')
        print(e)
        S.close()
    finally:
        #目的判断上面请求是否成功，未成功则返回None
        if ret == False:
            S.close()
            return None




def selenium_proxy():
    from selenium import webdriver
    ip = get_proxy()
    if ip:
        desired_capabilities = webdriver.DesiredCapabilities.INTERNETEXPLORER.copy()
        # Change the proxy properties of that copy.
        desired_capabilities['proxy'] = {
            "httpProxy": ip ,
            "noProxy": None,
            "proxyType": "MANUAL",
            "class": "org.openqa.selenium.Proxy",
            "autodetect": False
        }
        return desired_capabilities
    else:
        return None






def requests_proxy():
    """
    requests使用代理
    有数据返回数据
    没有数据返回空
    :return:
    """
    ip = get_proxy()
    # ip = None
    if ip != None:
        proxies = {"http": "http://{}".format(ip),
                   "https": "http://{}".format(ip), }
        return proxies
    else:
        return None









