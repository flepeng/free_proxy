# -*- coding:utf-8 -*-
"""
    @Time  : 2024/1/3 17:46
    @Author: lepeng feng
    @File  : check_proxy.py
    @Desc  : 检查传入的 proxy 是否能用
"""
import os
import sys
import time
import urllib
import codecs
import locale
import random
import socket
import requests
import subprocess
from src.get_proxy_ip.spiders import logger

if sys.version_info >= (3, 0):
    import queue
    import urllib.request

    build_opener = urllib.request.build_opener
    install_opener = urllib.request.install_opener
    quote = urllib.parse.quote
    urlopen = urllib.request.urlopen
    ProxyHandler = urllib.request.ProxyHandler
    Queue = queue.Queue
    Request = urllib.request.Request

    xrange = range
else:
    import Queue
    import urllib2

    build_opener = urllib2.build_opener
    install_opener = urllib2.install_opener
    quote = urllib.quote
    urlopen = urllib2.urlopen
    ProxyHandler = urllib2.ProxyHandler
    Queue = Queue.Queue
    Request = urllib2.Request

    # Reference: http://blog.mathieu-leplatre.info/python-utf-8-print-fails-when-redirecting-stdout.html
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


class Check(object):

    # 通过下列网站获取本机代理的ip地址
    IFCONFIG_CANDIDATES = (
        "https://api.ipify.org/?format=text",
        "https://myexternalip.com/raw",
        "https://wtfismyip.com/text",
        "https://icanhazip.com/",
        # "https://ipv4bot.whatismyipaddress.com/",
        # "https://ip4.seeip.org"
    )
    FALLBACK_METHOD = False
    USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
    timeout = 2  # 判断代理ip是否存活的超时时间。

    def _random_ifconfig(self):
        retval = random.sample(self.IFCONFIG_CANDIDATES, 1)[0]
        retval = retval.replace("https://", "http://")
        return retval

    def check_alive(self, address, port):
        """
        检查对应 ip和端口 是否存活
        :param address:
        :param port:
        :return:
        """
        result = False
        try:
            s = socket.socket()
            s.connect((address, int(port)))
            result = True
        except:
            pass
        finally:
            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except:
                pass
        return result

    def check_ip(self, proxy, handle=None):
        start_time = time.time()
        candidate = "%s://%s:%s" % (proxy["proto"], proxy["ip"], proxy["port"])
        url = self._random_ifconfig()

        if not self.FALLBACK_METHOD:
            command = "curl -m %d -A \"%s\" --proxy %s %s" % (self.timeout, self.USER_AGENT, candidate, url)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result, _ = process.communicate()
        elif proxy["proto"] in ("http", "https"):
            opener = build_opener(ProxyHandler({"http": candidate, "https": candidate}))
            try:
                req = Request(
                    "".join(url[i].replace(' ', "%20") if i > url.find('?') else url[i] for i in xrange(len(url))),
                    "", {"User-agent": self.USER_AGENT})
                retval = (urlopen if not opener else opener.open)(req, timeout=self.timeout).read()
            except Exception as ex:
                try:
                    retval = ex.read() if hasattr(ex, "read") else getattr(ex, "msg", str())
                except:
                    retval = None
            result = (retval or b"").decode("utf8")
        logger.debug("获取到结果：{}".format(result))

        if (result or "").strip() == proxy["ip"].encode("utf8"):
            latency = time.time() - start_time
            if latency < self.timeout:
                sys.stdout.write("\r%s%s # latency: %.2f sec; country: %s; anonymity: %s (%s)\n" % (candidate, " " * (32 - len(candidate)), latency, ' '.join(_.capitalize() for _ in (proxy["country"].lower() or '-').split(' ')), proxy["type"], proxy["anonymity"]))
                sys.stdout.flush()
                if handle:
                    os.write(handle, ("%s%s" % (candidate, os.linesep)).encode("utf8"))
                return True

    def check_proxy(self, proxy, handle=None):
        logger.debug("开始测试：{}".format(proxy))
        if not all((proxy["ip"], proxy["port"])):
            return

        if not self.check_alive(proxy["ip"], proxy["port"]):
            logger.debug("地址不通")
            return

        return self.check_ip(proxy, handle)

    def check_proxy_list(self, proxy_list, handle=None):
        ret = []
        try:
            for proxy in proxy_list:
                if self.check_proxy(proxy, handle):
                    ret.append(proxy)
            return ret
        except Exception as e:
            return ret


class CheckRequest(object):
    timeout = 5

    def check_proxy(self, proxy):
        logger.debug("开始测试：{}".format(proxy))
        try:
            if proxy.get("proto") == "https":
                # 设置代理服务器地址和端口号
                temp = {'https': 'https://{}:{}'.format(proxy.get("ip"), proxy.get("port"))}
                # 发送 GET 请求到目标网站（需要通过代理）
                response = requests.get('https://www.baidu.com', proxies=temp, timeout=self.timeout)
            elif proxy.get("proto") == "http":
                temp = {'http': 'http://{}:{}'.format(proxy.get("ip"), proxy.get("port"))}
                response = requests.get('http://www.baidu.com', proxies=temp, timeout=self.timeout)
            else:
                return

            if response.status_code == 200:
                logger.debug("代理可用")
                return True
            else:
                logger.debug(f"代理不可用，状态码为{response.status_code}")
                return
        except Exception as e:
            logger.exception("发生异常，代理不可用")
        return

    def check_proxy_list(self, proxy_list):
        ret = []
        try:
            for proxy in proxy_list:
                if self.check_proxy(proxy):
                    ret.append(proxy)
            return ret
        except Exception as e:
            return ret


if __name__ == "__main__":
    temp = [{'proto': 'http', 'ip': '47.109.57.93', 'port': 6969, 'country': '四川省成都市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '116.62.50.250', 'port': 7890, 'country': '浙江省杭州市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '116.62.50.250', 'port': 7890, 'country': '浙江省杭州市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.213.128.90', 'port': 8080, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '121.37.203.216', 'port': 3128, 'country': '广东省广州市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.219.43.134', 'port': 20201, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.106.144.184', 'port': 7890, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.104.79.145', 'port': 8499, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '115.29.140.201', 'port': 8889, 'country': '山东省青岛市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '180.103.127.9', 'port': 7890, 'country': '江苏省淮安市 电信', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '180.103.127.9', 'port': 7890, 'country': '江苏省淮安市 电信', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.55.49.231', 'port': 20000, 'country': '浙江省杭州市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '139.9.119.20', 'port': 80, 'country': '北京市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '139.224.56.162', 'port': 1234, 'country': '浙江省杭州市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.92.239.69', 'port': 8081, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.109.56.77', 'port': 1081, 'country': '四川省成都市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.92.248.86', 'port': 10000, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.209.253.237', 'port': 8999, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.98.134.232', 'port': 9992, 'country': '浙江省杭州市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.104.89.111', 'port': 8085, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '115.29.149.2', 'port': 8282, 'country': '山东省青岛市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.219.74.58', 'port': 1000, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.208.90.243', 'port': 8999, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '101.34.72.57', 'port': 7890, 'country': '上海市 腾讯云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '101.34.72.57', 'port': 7890, 'country': '上海市 腾讯云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.134.139.219', 'port': 8080, 'country': '广东省深圳市 ?', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.104.26.204', 'port': 8889, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '58.220.95.30', 'port': 10174, 'country': '江苏省扬州市 电信', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '123.56.129.203', 'port': 50001, 'country': '北京市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '47.106.107.212', 'port': 3128, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.106.107.212', 'port': 3128, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '121.37.207.154', 'port': 8999, 'country': '广东省广州市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.79.21.48', 'port': 3127, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '140.210.196.193', 'port': 8060, 'country': '贵州省贵阳市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.100.120.200', 'port': 7890, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.130.36.245', 'port': 8080, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.130.34.237', 'port': 8080, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.109.46.223', 'port': 5678, 'country': '四川省成都市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.92.242.45', 'port': 8999, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.109.52.147', 'port': 80, 'country': '四川省成都市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.101.65.228', 'port': 80, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '36.138.56.214', 'port': 3129, 'country': '甘肃省兰州市 移动', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '36.138.56.214', 'port': 3129, 'country': '甘肃省兰州市 移动', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '115.29.151.41', 'port': 8081, 'country': '山东省青岛市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.79.34.201', 'port': 30001, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '117.74.65.29', 'port': 8181, 'country': '北京市 北京华夏光网通信技术有限公司联通节点', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '61.130.9.37', 'port': 443, 'country': '浙江省杭州市萧山区 电信/教育网', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '115.182.212.177', 'port': 80, 'country': '北京市 鹏博士大数据有限公司北京分公司', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.92.248.197', 'port': 41890, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '123.57.1.78', 'port': 10443, 'country': '北京市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.79.16.132', 'port': 8080, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '123.60.139.197', 'port': 6969, 'country': '上海市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.113.230.224', 'port': 3333, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '117.74.65.215', 'port': 9443, 'country': '北京市 北京华夏光网通信技术有限公司联通节点', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '121.37.199.23', 'port': 8089, 'country': '广东省广州市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.134.138.108', 'port': 8888, 'country': '广东省深圳市 ?', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.113.219.226', 'port': 9091, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.104.57.170', 'port': 10001, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.213.129.20', 'port': 80, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.100.90.127', 'port': 4444, 'country': '上海市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '121.37.205.253', 'port': 999, 'country': '广东省广州市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '121.37.201.60', 'port': 8080, 'country': '广东省广州市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '121.40.115.140', 'port': 8080, 'country': '浙江省杭州市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '139.129.231.228', 'port': 5001, 'country': '山东省青岛市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '123.57.1.16', 'port': 59394, 'country': '北京市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.104.62.128', 'port': 9999, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.113.221.120', 'port': 1080, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.134.140.146', 'port': 9999, 'country': '广东省深圳市 ?', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.130.39.117', 'port': 8080, 'country': '安徽省六安市 电信', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.113.203.122', 'port': 41890, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '101.132.25.152', 'port': 50001, 'country': '上海市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '124.71.157.181', 'port': 8888, 'country': '上海市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.92.247.250', 'port': 10000, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.134.140.97', 'port': 443, 'country': '广东省深圳市 ?', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '112.124.2.212', 'port': 8888, 'country': '浙江省杭州市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '139.198.168.65', 'port': 7890, 'country': '上海市 青云数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '139.198.168.65', 'port': 7890, 'country': '上海市 青云数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '122.9.131.161', 'port': 3128, 'country': '贵州省贵阳市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.79.31.133', 'port': 52869, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '124.70.55.29', 'port': 20002, 'country': '北京市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.113.224.182', 'port': 83, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.46.197.14', 'port': 8083, 'country': '北京市 华为云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '139.196.214.238', 'port': 2087, 'country': '上海市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.134.136.224', 'port': 8080, 'country': '江苏省无锡市 电信', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.208.84.236', 'port': 8080, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.219.5.240', 'port': 8080, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'high', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '218.57.210.186', 'port': 9002, 'country': '山东省聊城市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.77.148.138', 'port': 8080, 'country': '浙江省杭州市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '111.177.63.86', 'port': 8888, 'country': '湖北省襄阳市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '111.177.63.86', 'port': 8888, 'country': '湖北省襄阳市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.100.254.82', 'port': 80, 'country': '上海市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '183.215.23.242', 'port': 9091, 'country': '湖南省长沙市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '117.160.250.131', 'port': 8899, 'country': '河南省 移动/数据上网公共出口', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '111.16.50.12', 'port': 9002, 'country': '山东省临沂市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '117.160.250.133', 'port': 8899, 'country': '河南省安阳市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '58.246.58.150', 'port': 9002, 'country': '上海市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '113.143.37.82', 'port': 9002, 'country': '陕西省宝鸡市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '60.12.168.114', 'port': 9002, 'country': '浙江省台州市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '36.134.91.82', 'port': 8888, 'country': '北京市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '113.208.119.142', 'port': 9002, 'country': '北京市 北京商务中心区通信科技有限公司', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '49.7.11.187', 'port': 80, 'country': '北京市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '123.233.245.158', 'port': 9080, 'country': '山东省济南市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '114.55.84.12', 'port': 30001, 'country': '浙江省杭州市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '58.253.210.122', 'port': 8888, 'country': '广东省清远市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.100.91.57', 'port': 8080, 'country': '上海市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '122.9.4.213', 'port': 80, 'country': '北京市 华为云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '111.20.217.178', 'port': 9091, 'country': '陕西省 移动/全省通用', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '60.214.128.150', 'port': 9091, 'country': '山东省 BGP大带宽业务机柜段', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '61.175.214.2', 'port': 9091, 'country': '浙江省温州市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '60.210.40.190', 'port': 9091, 'country': '山东省淄博市 广电网', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '112.53.184.170', 'port': 9091, 'country': '四川省 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.107.61.215', 'port': 8000, 'country': '广东省深圳市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '183.230.162.122', 'port': 9091, 'country': '重庆市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '58.20.235.231', 'port': 9002, 'country': '湖南省湘潭市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '111.26.177.28', 'port': 9091, 'country': '吉林省 移动/全省通用', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '139.224.190.222', 'port': 8083, 'country': '浙江省杭州市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '112.51.96.118', 'port': 9091, 'country': '福建省三明市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '125.94.219.96', 'port': 9091, 'country': '广东省韶关市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'https', 'ip': '123.126.158.50', 'port': 80, 'country': '北京市 联通数据中心', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '123.126.158.50', 'port': 80, 'country': '北京市 联通数据中心', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '58.20.248.139', 'port': 9002, 'country': '湖南省郴州市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.197.40.219', 'port': 9002, 'country': '广东省广州市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '221.6.139.190', 'port': 9002, 'country': '江苏省常州市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.93.114.68', 'port': 88, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.165.0.137', 'port': 9002, 'country': '河南省 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.107.89.178', 'port': 80, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.234.203.171', 'port': 9002, 'country': '广东省广州市番禺区 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '222.138.76.6', 'port': 9002, 'country': '河南省开封市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '117.160.250.134', 'port': 8899, 'country': '河南省安阳市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '220.248.70.237', 'port': 9002, 'country': '上海市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '117.160.250.138', 'port': 8899, 'country': '河南省安阳市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '223.113.80.158', 'port': 9091, 'country': '江苏省徐州市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '60.188.102.225', 'port': 18080, 'country': '浙江省台州市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '61.133.66.69', 'port': 9002, 'country': '山东省菏泽市 联通', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.107.33.254', 'port': 8090, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '39.105.5.126', 'port': 80, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '139.159.176.147', 'port': 8090, 'country': '广东省广州市 华为云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '8.219.97.248', 'port': 80, 'country': '中国 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.26.0.11', 'port': 8880, 'country': '浙江省杭州市 阿里巴巴网络有限公司BGP数据中心(BGP)', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '182.92.73.106', 'port': 80, 'country': '北京市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '222.179.155.90', 'port': 9091, 'country': '重庆市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '223.100.178.167', 'port': 9091, 'country': '辽宁省本溪市 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '43.138.20.156', 'port': 80, 'country': '北京市 腾讯云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '182.106.220.252', 'port': 9091, 'country': '江西省南昌市 电信', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '47.100.254.82', 'port': 80, 'country': '上海市 阿里云', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '60.210.40.190', 'port': 9091, 'country': '山东省淄博市 广电网', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '120.234.203.171', 'port': 9002, 'country': '广东省广州市番禺区 移动', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '14.103.24.20', 'port': 8000, 'country': '广东省广州市 鹏博士', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}, {'proto': 'http', 'ip': '114.55.84.12', 'port': 30001, 'country': '浙江省杭州市 阿里云BGP数据中心', 'supplier': '', 'type': '', 'anonymity': 'common', 'source': 'http://www.kxdaili.com/dailiip/1/'}]
    ret = CheckRequest().check_proxy_list(temp)
    print(ret)
