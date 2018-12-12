# Python 最新模拟登录新浪微博  支持验证码和保存 Cookies
> 网上大部分对微博的爬虫都是先人工登陆获取cookie再进行接下来的抓取操作的，所以我写了一份模拟登陆获取cookie的（因为是分析为主要目的，所以纯手动构建cookie，没有使用requests.session），并实现了提交验证码，
本文我对分析过程和代码进行步骤分解，完整的代码请见末尾 Github 仓库，不过还是建议看一遍正文，因为代码早晚会失效，解析思路才是永恒。

## 分析 POST 请求
首先打开控制台正常登录一次，可以很快找到登录的 API 接口，这个就是模拟登录 POST 的链接。

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51751_1.png)

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51756_5.png)

我们要构建header 和 Formdata

## 构建 Headers

观察POST请求的header发现header里面已经含有cookie了

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51751_2.png)

翻看之前的请求，容易发现SSO-DBL来自一个叫prelogin的请求，这个请求在输入完用户名，鼠标点击输入密码的文本框是触发

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51752_3.png)

ULOGIN_IMG则是请求验证码图片的时候获取的,而获取验证码又要带值为SSO-DBL的cookie进行请求

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51752_4.png)

至此POST请求的header已经构建好了，其他的复制黏贴即可

## 构建 Form-Data

未完待续

