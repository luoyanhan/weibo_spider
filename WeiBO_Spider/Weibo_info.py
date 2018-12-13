import requests
import re
from Login import login


class WeiBo:
    def __init__(self, cookie, userids):
        self.session = requests.Session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
            'Cookie': cookie
        }
        self.userids = userids

    def get_username_number(self, uid):
        user_url = 'https://weibo.com/p/100306{0}/info'.format(uid)
        response = self.session.get(user_url)
        # print(response.text)
        # 获取个人信息
        infoStr = re.findall(r'<span class=\\"pt_detail\\">([\s\S]*?)<\\/span>', response.text)
        name = infoStr[0].strip()
        location = infoStr[1].strip()
        sex = infoStr[2].strip()
        summery = infoStr[3].strip()
        signup_time = re.search(r'(\d+-\d+-\d+)', infoStr[4]).group(1)
        # print((name, location, sex, summery, signup_time))
        # 获取关注，微博，粉丝数
        numberStr = re.search(r'(<table class=\\"tb_counter\\" cellpadding=\\"0\\" cellspacing=\\"0\\">[\s\S]*?<\\/table>)', response.text).group(1)
        li = re.findall(r'<strong class=\\"W_f16\\">(\d+)<\\/strong>', numberStr)
        guanzhu, fans, weibo_num = li
        print(guanzhu, fans, weibo_num)
        return (name, location, sex, summery, signup_time, guanzhu, fans, weibo_num)


if __name__ == "__main__":
    cookie = login()
    weibo = WeiBo(cookie, ['2386774894'])
    weibo.get_username_number('2386774894')