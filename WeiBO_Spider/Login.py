import requests
import base64
import time
import json
import re
import os
import rsa
import binascii
import random
from PIL import Image
from urllib.parse import urlencode
from config import USERNAME, PASSWORD

BASEURL = 'https://login.sina.com.cn/sso/prelogin.php?'
Headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
}


def prelogin():
    pre_url = 'https://login.sina.com.cn/sso/prelogin.php?'
    par = {
        'entry': 'weibo',
        'callback': 'sinaSSOController.preloginCallBack',
        'rsakt': 'mod',
        'checkpin': '1',
        'client': 'ssologin.js(v1.4.19)',
    }
    nowtime = int(round(time.time()*1000))
    par['_'] = nowtime
    su = base64.b64encode(USERNAME.encode('utf-8'))
    su = str(su, encoding='utf-8')
    par['su'] = su
    url = pre_url + urlencode(par)
    response = requests.get(url, headers=Headers)
    pre_setcookie = response.headers['set-cookie'].split(';')[0]
    Json = re.search(r'preloginCallBack\(([\s\S]*?)\)', response.text).group(1)
    result = json.loads(Json)
    return pre_setcookie, su, result['pcid'], result['nonce'], result['rsakv'], result['pubkey']

def get_chaptcha(cookie, pcid):
    chaptcha_url = 'https://login.sina.com.cn/cgi/pin.php?'
    par = {
        'p': pcid,
        'r': '3317570',
        's': '0'
    }
    url = chaptcha_url + urlencode(par)
    headers = Headers.copy()
    headers['Referer'] = 'https://weibo.com/'
    headers['Cookie'] = cookie
    headers['Host'] = 'login.sina.com.cn'
    img = requests.get(url, headers=headers)
    chaptcha_setcookie = img.headers['set-cookie'].split(';')[0]
    with open('chaptcha.png', 'wb') as f:
        f.write(img.content)
    fp = open('chaptcha.png', 'r')
    im = Image.open('chaptcha.png')
    im.show()
    door = input('请输入验证码： ')
    fp.close()
    os.remove('chaptcha.png')
    return door, chaptcha_setcookie

def get_sp(pubkey, servertime, nonce, password):
    rsaPublickey = int(pubkey, 16)
    para2 = int('10001', 16)
    key = rsa.PublicKey(rsaPublickey, para2)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    message = message.encode('utf-8')
    sp = rsa.encrypt(message, key)
    sp = binascii.b2a_hex(sp)
    sp = str(sp, encoding='utf-8')
    return sp

def redirect_login(dict_cookie, login_cookie, redirect_url):
    new_cookielist = []
    for item in dict_cookie.items():
        new_cookielist.append(item[0] + '=' + item[1])
    new_cookie = '; '.join(new_cookielist)
    new_cookie = login_cookie + '; ' + new_cookie
    headers = Headers.copy()
    headers['Cookie'] = new_cookie
    headers['Host'] = 'login.sina.com.cn'
    headers['Referer'] = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
    response = requests.get(redirect_url, headers=headers)
    finalurl = re.search(r"'login',function\(\){location.replace\('([\s\S]*?)'\);}\);}", response.text).group(1)
    Str = re.search(r'sinaSSOController.setCrossDomainUrlList\(([\s\S]*?)\);}', response.text).group(1)
    new_url = json.loads(Str)["arrURL"][0]+'&'
    par = {
        '_': int(round(time.time()*1000)),
        'callback': 'sinaSSOController.doCrossDomainCallBack',
        'client': 'ssologin.js(v1.4.19)',
        'scriptId': 'ssoscript0'
    }
    new_url = new_url + urlencode(par)
    headers = Headers.copy()
    headers['Referer'] = redirect_url
    headers['Host'] = 'passport.weibo.com'
    response = requests.get(new_url, headers=headers)

    cookie_list = []
    for item in requests.utils.dict_from_cookiejar(response.cookies).items():
        cookie_list.append(item[0] + '=' + item[1])
    finalcookie = '; '.join(cookie_list)
    headers['Cookie'] = finalcookie
    final_response = requests.get(finalurl, headers=headers, allow_redirects=False)
    location = final_response.headers['Location']
    return requests.utils.dict_from_cookiejar(final_response.cookies), location

def login():
    login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
    FormData = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '0',
        'qrcode_flag': 'false',
        'useticket': '1',
        'pagerefer': 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)',
        'pcid': '',
        'door': '',
        'vsnf': '1',
        'su': '',
        'service': 'miniblog',
        'servertime': '',
        'nonce': '',
        'pwencode': 'rsa2',
        'rsakv': '',
        'sp': '',
        'sr': '1536*864',
        'encoding': 'UTF - 8',
        'prelt': str(random.randint(20, 200)),
        'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    pre_setcookie, su, pcid, nonce, rsakv, pubkey = prelogin()
    FormData['pcid'] = pcid
    FormData['su'] = su
    servertime = int(round(time.time()))
    FormData['servertime'] = servertime
    FormData['nonce'] = nonce
    FormData['rsakv'] = rsakv
    door, chaptcha_setcookie = get_chaptcha(pre_setcookie, pcid)
    FormData['door'] = door
    sp = get_sp(pubkey, servertime, nonce, PASSWORD)
    FormData['sp'] = sp
    login_cookie = '; '.join([pre_setcookie, chaptcha_setcookie])
    headers = Headers.copy()
    headers['Host'] = 'login.sina.com.cn'
    headers['Referer'] = 'https://weibo.com/'
    headers['Cookie'] = login_cookie
    response = requests.post(login_url, headers=headers, data=FormData)
    dict_cookies = requests.utils.dict_from_cookiejar(response.cookies)
    redirect_url = re.search(r'location.replace\("([\s\S]*?)"\);', response.text).group(1)
    finalcookie_one, location = redirect_login(dict_cookies, login_cookie, redirect_url)
    headers = Headers.copy()
    headers['Host'] = 'weibo.com'
    headers['Referer'] = redirect_url
    cookie_list = []
    for key in ['SCF', 'SSOLoginState', 'SUB', 'SUBP', 'SUHB']:
        if key == 'SSOLoginState':
            cookie_list.append(key + '=' + finalcookie_one['SRF'])
        else:
            cookie_list.append(key+'='+finalcookie_one[key])
    cookie = '; '.join(cookie_list)
    headers['Cookie'] = cookie
    get_Ugrow_request = requests.get(location, headers=headers)
    homecookie = cookie+'; '+'Ugrow-G0='+requests.utils.dict_from_cookiejar(get_Ugrow_request.cookies)['Ugrow-G0']+'; '+'un='+USERNAME
    message = re.search(r'"uniqueid":"([\s\S]*?)",[\s\S]*?"userdomain":"([\s\S]*?)"}}', get_Ugrow_request.text)
    id = message.group(1)
    domain = message.group(2)
    home_url = 'https://weibo.com/u/'+id+'/home'+domain
    headers = Headers.copy()
    headers['Cookie'] = homecookie
    headers['Host'] = 'weibo.com'
    headers['Referer'] = 'https://weibo.com/'
    response = requests.get(home_url, headers=headers)
    cookie_li = []
    cookie_dict = requests.utils.dict_from_cookiejar(response.cookies)
    for key in cookie_dict:
        cookie_li.append(key+'='+cookie_dict[key])
    homecookie = homecookie+'; '+'; '.join(cookie_li)

    if not os.path.exists('./cookies.txt'):
        with open(r'./cookies.txt', 'w') as f:
            f.write(homecookie)

    return homecookie



if __name__ == "__main__":
    homecookie = login()
    headers = Headers.copy()
    headers['Cookie'] = homecookie
    response = requests.get('https://weibo.com/u/2386774894?is_all=1', headers=headers)
    print(response.text)
