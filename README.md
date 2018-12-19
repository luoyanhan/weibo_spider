# Python 新浪微博爬虫，支持模拟登陆
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

翻看之前的请求，容易发现SSO-DBL来自一个叫prelogin的请求，这个请求在输入完用户名，鼠标点击输入密码的文本框时触发

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51752_3.png)

ULOGIN_IMG则是请求验证码图片的时候获取的,而获取验证码又要带值为SSO-DBL的cookie进行请求

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51752_4.png)

我们来看prelogin请求的参数

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51848_6.png)

值得关注的是那串数字和su，其余我们估计是固定参数，仔细观察发现那串数字其实是一个13位时间戳，直接使用time模块即可。接下来就要构造su了，Ctrl+F全局搜索
输入'su:'

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A52033_1.png)

找到构造su的js代码，发现是将用户名进行编码得到的使用bs64模块构造即可。

这样我们就完成了prelogin请求的header和参数构造，可以获得SSO-DBL了

接下来分析验证码图片的请求参数

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51848_7.png)

其中s是固定值，r经测试可以反复使用同一个值，所以只有p是需要获取的，而p可以在刚才prelogin的response中找到

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51848_8.png)

至此POST请求的header已经构建好了，其他的复制黏贴即可

## 构建 Form-Data

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A51756_5.png)

这里nonce, pcid, rsakv都可以在prelogin的response里找到，door是验证码，prelt是随机数，所以每次用同一个就行，servertime是时间戳

值得关注的是sp,老办法Ctrl+F找到构造的js代码

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8812%E6%97%A52106_2.png)

发现这里使用了rsa算法加密，这里的公钥用了从prelogin里返回的一个叫pubkey的16进制数和16进制的10001共同生成，再将包含servertime，刚才提到的nonce,和用户密码的字符串进行加密得出sp,具体实现可以看代码。

到这里所有参数已经找齐了，模拟POST请求即可。

我们可以看到POST请求成功后我们的cookie更新了一大堆值

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8815%E6%97%A51121_1.png)

将这些值取出来后可以更新我们的cookie。

到了这里本来以为已经大功告成，我们找到登陆成功的html请求

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8815%E6%97%A51135_3.png)

看他的请求cookie

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8815%E6%97%A51135_4.png)

发现其中一些值和我们找到的有很大出入，说明之前cookie又发生改变了。我们耐心地往上翻请求，看看新出现的以及改变了值的cookie都在哪些请求中产生。

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8815%E6%97%A51143_5.png)

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8815%E6%97%A51143_6.png)

![Image text](https://github.com/luoyanhan/weibo_spider/blob/master/WeiBO_Spider/Image/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE18%E5%B9%B412%E6%9C%8815%E6%97%A51149_7.png)

发现我们需要找的变化了的cookie值都可以在这几个请求中找到，用之前的方法模拟请求并且抓下来即可。其中有一些请求的url和参数是每次都不同的，但是也能在我们之前发送的一些请求的response里找得到，用正则匹配出来即可。

至此我们已经完成了最终home请求所需cookie的构造，模拟请求并获得最终登陆成功的cookie即可。

