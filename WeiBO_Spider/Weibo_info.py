import requests
import re
import json
import os
from Login import login
from urllib.parse import urlencode
from bs4 import BeautifulSoup

class WeiBo:
    def __init__(self, cookie, userids):
        self.session = requests.Session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
            'Cookie': cookie
        }
        self.userids = userids
        self.page_num = 0

    def get_username_number(self, uid):
        user_url = 'https://weibo.com/{0}/info'.format(uid)
        response = self.session.get(user_url)
        # 获取个人信息
        infoStr = re.search(r'<ul class=\\"clearfix\\">([\s\S]*?)<\\/ul>', response.text).group(1)
        lis = re.findall(r'<li [\s\S]*?>([\s\S]*?)<\\/li>', infoStr)
        info = ''
        for li in lis:
            key = re.search(r'<span class=\\"pt_title S_txt2\\">([\s\S]*?)<\\/span>', li).group(1).strip()
            if key == '博客：':
                value = re.search(r'<a [\s\S]*?>([\s\S]*?)<\\/a>', li).group(1).replace(r'\/', '/').strip()
            elif key == '注册时间：':
                value = re.search(r'(\d+-\d+-\d+)', li).group(1).strip()
            else:
                value = re.search(r'<span class=\\"pt_detail\\">([\s\S]*?)<\\/span>', li).group(1).strip()
            info += key+value+'\n'
        # 获取关注，微博，粉丝数
        numberStr = re.search(r'(<table class=\\"tb_counter\\" cellpadding=\\"0\\" cellspacing=\\"0\\">[\s\S]*?<\\/table>)', response.text).group(1)
        li = re.findall(r'<strong [\s\S]*?">(\d+)<\\/strong>', numberStr)
        guanzhu, fans, weibo_num = li
        hrefs = re.findall(r'<a[\s\S]*?href=\\"([\s\S]*?)\\" >', numberStr)
        guanzhu_href = 'https:' + hrefs[0].replace('\\', '')
        fans_href = 'https:' + hrefs[1].replace('\\', '')
        # print(guanzhu_href)
        # print(fans_href)
        return (info, guanzhu, fans, weibo_num, guanzhu_href, fans_href), guanzhu_href, fans_href

    def get_weibo_url(self, uid, page):
        url_list = []
        try:
            url1 = 'https://weibo.com/p/100306{0}/home?'.format(uid)
            par1 = {
                'pids': 'Pl_Official_MyProfileFeed__22',
                'is_all': '1',
                'profile_ftype': '1',
                'page': page,
                'ajaxpagelet': '1',
                'ajaxpagelet_v6': '1',
            }
            # print(url1+urlencode(par1))
            response1 = self.session.get(url1+urlencode(par1))
            li1 = re.match(r'<script>parent.FM.view\(([\s\S]*?)\)</script>', response1.text).group(1)
            html1 = json.loads(li1)['html']
            soup1 = BeautifulSoup(html1, 'lxml')
            for div in soup1.find_all('div', attrs={'class': 'WB_from'}):
                detail_url = div.find_all('a')[0]['href']
                # if '?' in detail_url:
                #     url_list.append(detail_url)
                url_list.append(detail_url)

            url2 = 'https://weibo.com/p/aj/v6/mblog/mbloglist?'
            par2 = {
                'ajwvr': '6',
                'domain': '100306',
                'is_all': '1',
                'profile_ftype': '1',
                'page': page,
                'pagebar': '0',
                'pl_name': 'Pl_Official_MyProfileFeed__22',
                'id': '100306'+uid,
                'script_uri': '/p/100306{0}/home'.format(uid),
                'feed_type': '0',
                'pre_page': page,
                'domain_op': '100306',
            }
            # print(url2 + urlencode(par2))
            response2 = self.session.get(url2 + urlencode(par2))
            html2 = json.loads(response2.text)['data']
            soup2 = BeautifulSoup(html2, 'lxml')
            for div in soup2.find_all('div', attrs={'class': 'WB_from'}):
                detail_url = div.find_all('a')[0]['href']
                # if '?' in detail_url:
                #     url_list.append(detail_url)
                url_list.append(detail_url)

            url3 = 'https://weibo.com/p/aj/v6/mblog/mbloglist?'
            par3 = {
                'ajwvr': '6',
                'domain': '100306',
                'is_all': '1',
                'profile_ftype': '1',
                'page': page,
                'pagebar': '1',
                'pl_name': 'Pl_Official_MyProfileFeed__22',
                'id': '100306' + uid,
                'script_uri': '/p/100306{0}/home'.format(uid),
                'feed_type': '0',
                'pre_page': page,
                'domain_op': '100306',
            }
            response3 = self.session.get(url3 + urlencode(par3))
            html3 = json.loads(response3.text)['data']
            soup3 = BeautifulSoup(html3, 'lxml')
            for div in soup3.find_all('div', attrs={'class': 'WB_from'}):
                detail_url = div.find_all('a')[0]['href']
                # if '?' in detail_url:
                #     url_list.append(detail_url)
                url_list.append(detail_url)
            if page == 1:
                pages = soup3.find_all('a', attrs={'bpfilter': 'page'})
                page_num = re.search(r'(\d+)', pages[0].string).group(1)
                self.page_num = int(page_num)
            return url_list
        except:
            pass

    def get_weibo(self, url):
        try:
            response = self.session.get('https://weibo.com'+url)
            html = re.search(r'<script>FM.view\(({"ns":"pl.content.weiboDetail.index"[\s\S]*?)\)</script>', response.text).group(1)
            html = json.loads(html)['html']
            soup = BeautifulSoup(html, 'lxml').find('div', attrs={'node-type': 'feed_list_content'})
            weibo_text = ''
            for child in soup.children:
                text = child.string
                if text:
                    weibo_text += text.strip()+'\n'
            print(weibo_text)
            return weibo_text
        except:
            pass

    def get_fans(self, url):
        pass

    def get_guanzhu(self, url):
        count = 1
        response = self.session.get(url)
        pages = re.search(r'(<div class=\\"W_pages\\">[\s\S]*?<\\/div>)', response.text).group(1)

        soup = BeautifulSoup(pages, 'lxml').find_all('a')[-1]
        next_page = None
        if '下一页' in str(soup):
            next_page = 'https://weibo.com' + soup.get('href').replace('\\"', '').replace('\\', '')

        uids = []
        guanzhu_li = re.findall(r'(<div class=\\"info_name[\s\S]*?>[\s\S]*?<\\/div>)', response.text)
        for i in guanzhu_li:
            soup = BeautifulSoup(i, 'lxml')
            a = soup.find('a', attrs={'class': '\\"S_txt1\\"'})
            userid = a.get('usercard')
            if userid:
                uids.append(re.search(r'id=(\d+)&', userid).group(1))
            else:
                uids.append(None)

        while next_page:
            count += 1
            # 新浪规定非互相关注的话只能看前五页关注列表
            if count > 5:
                break
            response = self.session.get(next_page)
            pages = re.search(r'(<div class=\\"W_pages\\">[\s\S]*?<\\/div>)', response.text).group(1)
            soup = BeautifulSoup(pages, 'lxml').find_all('a')[-1]
            next_page = None
            if '下一页' in str(soup) and soup.get('href'):
                next_page = 'https://weibo.com' + soup.get('href').replace('\\"', '').replace('\\', '')

            guanzhu_li = re.findall(r'(<div class=\\"info_name[\s\S]*?>[\s\S]*?<\\/div>)', response.text)
            for i in guanzhu_li:
                soup = BeautifulSoup(i, 'lxml')
                a = soup.find('a', attrs={'class': '\\"S_txt1\\"'})
                userid = a.get('usercard')
                if userid:
                    uids.append(re.search(r'id=(\d+)&', userid).group(1))
                else:
                    uids.append(None)
        print(len(uids))
        return uids


    def start(self):
        count = 0
        for id in self.userids:
            if os.path.exists(r'./{0}.txt'.format(id)):
                os.remove(r'./{0}.txt'.format(id))
            f = open(r'./{0}.txt'.format(id), 'a', encoding='utf-8')
            info, guanzhu_href, fans_href = self.get_username_number(id)
            f.write(str(info)+'\n')
            f.flush()
            self.get_guanzhu(guanzhu_href)
            url_list = self.get_weibo_url(id, 1)

            for url in url_list:
                weibo_text = self.get_weibo(url)
                f.write(weibo_text+'\n')
                f.flush()
                count += 1
                print(count)
            if self.page_num > 1:
                for page in range(2, self.page_num+1):
                    url_list = self.get_weibo_url(id, page)
                    for url in url_list:
                        try:
                            weibo_text = self.get_weibo(url)
                            f.write(weibo_text + '\n')
                            f.flush()
                        except:
                            pass
                        count += 1
                        print(count)
            f.close()





if __name__ == "__main__":
    if os.path.exists(r'./cookies.txt'):
        with open(r'./cookies.txt', 'r') as f:
            cookie = f.read()
    else:
        cookie = login()
    weibo = WeiBo(cookie, ['2386568184', '2386774894', '1264046551'])
    weibo.start()
