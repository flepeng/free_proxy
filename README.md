<h1 align="center">Free - Proxy</h1>

<p align="center">获取全网免费代理IP库 | Free Proxy</p>

***

# 项目介绍

采集全网 免费代理的资源，为爬虫提供有效的IP代理。


# 警告

本项目收集的免费代理IP均收集自互联网，本项目不对免费代理的有效性负责，请合法使用免费代理，由用户使用免费代理IP带来的法律责任与本项目无关。


# 使用

1.  下载源码:

    ```
    https://github.com/flepeng/free_proxy.git
    ```

2.  安装依赖:

    ```
    pip install *r requirements.txt
    ```
  
3.  运行

    ```
    python src/spider/spiders.py
    ```

4.  结果

    ![](/docs/imgs/result.png)

5.  检查代理是否可用。将上一步获取的代理复制到 check_proxy.py 文件中，然后运行

    ![](/docs/imgs/result02.png)


# 项目收集的代理网站

## 目前可用的代理网址

下列所示的代理网址本项目已全部收集，如果有更多的网站，可以在 spider.py 文件中自己添加


### 已收录的网站

*   快代理
    *   [收费的](https://www.kuaidaili.com/)
    *   [免费的私密](https://www.kuaidaili.com/free/dps/), ☆
    *   [免费的高匿](https://www.kuaidaili.com/free/inha), ☆
    *   [免费的透明](https://www.kuaidaili.com/free/intr), ☆
    *   [免费高速HTTP代理IP列表](https://www.kuaidaili.com/ops/proxylist/), ☆

*   米扑代理
    *   [收费的](https://proxy.mimvp.com/)
    *   [免费的](https://proxy.mimvp.com/freesecret) ★：免费的代理只能看10个，而且是从晚上扫描来的，可用的很少
    
*   开心代理
    *   [收费的](http://www.kxdaili.com/)
    *   [免费的高匿](http://www.kxdaili.com/dailiip/1/1.html)★：免费代理是通过网络扫描得来
    *   [免费的普匿](http://www.kxdaili.com/dailiip/2/1.html)★：免费代理是通过网络扫描得来
 
*   66IP代理
    *   [收费的](http://www.66daili.cn/)
    *   [免费的](http://www.66ip.cn) 基本上都不能用

*   89免费代理 
    *   [免费的](https://www.89ip.cn/)☆
   
*   云代理IP
    *   [免费的高匿](http://www.ip3366.net/free/?stype=1)★
    *   [免费的透明 or 普匿](http://www.ip3366.net/free/?stype=2')★

*   小幻代理
    *   [免费的](https://ip.ihuan.me/)★★:代理地址很多

*   无忧代理
    *   [收费的](https://www.data5u.com/)


### 未收录的

*   齐云代理IP
    *   https://proxy.ip3366.net/free/

*   atomintersoft
    *   https://www.atomintersoft.com/high_anonymity_elite_proxy_list
    *   http://www.atomintersoft.com/transparent_proxy_list
    *   http://www.atomintersoft.com/anonymous_proxy_list

*   IP海代理
    *   http://www.iphai.com/free/ng  # 国内高匿
    *   http://www.iphai.com/free/np  # 国内普通
    *   http://www.iphai.com/free/wg  # 国外高匿
    *   http://www.iphai.com/free/wp  # 国外普通

*   proxy list
    *   https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1

*   coolproxy
    *   https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:/page:2
    
*   proxy11
    *   https://proxy11.com/free-proxy/anonymous
    *   https://proxy11.com/api/demoweb/proxy.json?country=cn
    *   https://proxy11.com/api/demoweb/proxy.json?country=hk
    *   https://proxy11.com/api/demoweb/proxy.json?country=tw

*   proxydb
    *   http://proxydb.net/

*   站大爷
    *   https://www.zdaye.com/free/?
    *   https://www.zdaye.com/dayProxy/1.html

*   https://proxyhub.me/
*   https://cool-proxy.net/proxies.json


### txt 类型的网站

*   https://openproxylist.xyz/all.txt
*   http://ab57.ru/downloads/proxyold.txt
*   http://proxy.ipcn.org/proxylist2.html
*   https://www.proxy-list.download/api/v1/get?type={key}&_t={str(time.time())} {"http": 1, "socks4": 3, "socks5": 4} 


### git 相关

仓库地址                                | 状态                   | 文件名 | url 示例
--------------------------------------- | ---------------------- | ------ | --------
https://github.com/a2u/free-proxy-list  | 到2024年，4年未更新了。| free-proxy-list.txt | https://raw.githubusercontent.com/a2u/free-proxy-list/main/free-proxy-list.txt
https://github.com/parserpp/ip_ports/   | 到2024年，目前还在更新 |  proxyinfo.txt | https://raw.githubusercontent.com/parserpp/ip_ports/main/proxyinfo.txt
https://github.com/zevtyardt/proxy-list | 到2024年，目前还在更新 | all.txt、http.txt、socks4.txt、socks5.txt | https://raw.githubusercontent.com/zevtyardt/proxy-list/main/all.txt
https://github.com/monosans/proxy-list  | 到2024年，目前还在更新 | http.txt、socks4.txt、socks5.txt | https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt


## 无效或开始收费的代理

*   蝶鸟IP
    *   https://www.dieniao.com/。收费

*   free proxy
    *   https://www.freeproxylists.net/zh/。已失效
    *   http://www.proxylists.net/http_highanon.txt。已失效
    *   http://www.proxylists.net/?HTTP。已失效

*   360代理
    *   http://www.swei360.com。已经不做代理了

*   全网IP代理
    *   http://www.goubanjia.com。已失效，域名出售

*   蘑菇
    *   http://www.mogumiao.com/web。不做代理了

*   西刺IP代理
    *   https://www.xicidaili.com/nn，高匿。已失效
    *   https://www.xicidaili.com/nt，透明。已失效

*   有代理
    *   http://www.youdaili.net/Daili/http/。已失效，访问无反应

*   coderbusy
    *   https://proxy.coderbusy.com/classical/anonymous-type/highanonymous.aspx?page=1

*   无忧代理
    *   http://www.xdaili.cn/freeproxy.html。已失效，访问无反应

*   ipidea
    *   https://www.ipidea.net/

*   89免费代理
    *   https://www.89icn/index_1.html
    
*   万能代理
    *   http://wndaili.cn/。已失效，访问无反应

*   不知道名的代理
    *   https://www.freeproxylist.xyz。已失效
    *   https://getfreeproxylists.blogspot.com。已失效
    *   http://www.proxy360.cn/default.aspx。已失效
    *   http://ip.jiangxianli.com/。已失效
    *   http://www.proxy4free.info/。已失效
    *   http://tools.rosinstrument.com/proxy/plab100.xml。已失效
    *   https://www.rmccurdy.com/scripts/proxy/good.txt。已失效
    *   http://best-proxy.ru/feed。已失效
    *   http://uks.pl.ua/script/getproxy.php?last。已失效
    *   http://www.mimiip.com。已转行，不做代理了。
    *   http://www.ip181.com/。已失效，访问无反应
    *   http://www.feilongip.com/。已失效，访问无反应
    *   http://www.xiaohexia.cn。已失效，访问无反应
    *   https://proxy.peuland.com/proxy/search_proxy.php。已失效，访问无反应
    *   https://proxy.mimvcom/freeopen。已失效，访问无反应
    *   https://proxy.mimvcom/freesole。已失效，访问无反应
    *   https://proxy.mimvcom/freesecret。已失效，访问无反应
    *   https://proxy-list.org/english/index.php。已失效，访问无反应
    *   https://pzzqz.com/。已失效，访问无反应
    *   http://cn-proxy.com/。已失效，访问无反应
    *   http://nntime.com/。已失效，访问无反应
    *   http://www.nimadaili.com/gaoni/。已失效，访问无反应
    *   http://proxylist.fatezero.org/proxy.list?。已失效，访问无反应
    *   http://gatherproxy.com/。已失效，访问无反应
    *   https://hidemy.name/en/proxy-list。已失效，访问无反应
    *   http://www.3464.com/data/Proxy/http/。已失效，访问无反应
    *   https://proxy.seofangfa.com/。已失效，访问无反应
    *   http://www.xiladaili.com/https/。已失效，访问无反应
    *   http://www.xsdaili.cn/。已失效，访问无反应
    *   http://ip.yqie.com/ipproxy.htm。别访问，钓鱼的
    *   http://www.qydaili.com/free/?。已失效，访问无反应
    *   https://www.sslproxies.org/。已失效，访问无反应
    *   https://free-proxy-list.net/anonymous-proxy.html。已失效，访问无反应
    *   http://www.proxy-daily.com。已失效，访问无反应
    *   https://www.socks-proxy.net。已失效，访问无反应
    *   https://www.us-proxy.org。已失效，访问无反应
    *   https://www.sslproxies.org。已失效，访问无反应
    
*   不好用的
    *   https://zj.v.api.aa1.cn/api/proxyip/。不好用
    *   https://ip.uqidata.com/free/index.html 不更新了
    *   https://www.beesproxy.com/free 首页不显示。
    *   https://proxylist.geonode.com/api/proxy-list? 没权限
    *   http://www.pachongdaili.com/free/freelist1.html。不更新了

