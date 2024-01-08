# -*- coding:utf-8 -*-
"""
    @Time  : 2024/1/3 10:58
    @Author: lepeng feng
    @File  : spider.py
    @Desc  :
"""
import time
import requests
import asyncio
import aiohttp
import logging
import urllib3
from typing import List, Iterable
from bs4 import BeautifulSoup

from src.get_proxy_ip.proxy_enum import AnonymityEnum, ProxyTypeEnum
from src.get_proxy_ip.proxy_entity import ProxyEntity

urllib3.disable_warnings()
spider_collection = {}
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}


def get_logger():
    """
    创建日志单例
    """
    formatter = logging.Formatter("%(asctime)s %(name)s:%(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger("monitor")
    logger.setLevel(logging.DEBUG)
    handler_stream = logging.StreamHandler()
    handler_stream.setLevel(logging.DEBUG)
    handler_stream.setFormatter(formatter)
    logger.addHandler(handler_stream)
    return logger


logger = get_logger()


def spider_register(cls):
    spider_collection.update({cls.__name__: cls()})
    logger.info(f'注册{cls.__name__}')
    return cls


class AbsSpider(object):

    def __init__(self, name='unknown') -> None:
        self._name = name
        self._urls = []
        self._page_now = 1
        self._page_limit = 1
        self._page_list = []
        self._interval = 0
        self._encoding = 'utf-8'
        self._headers = HEADERS

    def get_urls(self) -> List[str]:
        """
        :return:
        """
        raise self._urls

    def get_encoding(self):
        """
        默认页面编码
        :return:
        """
        return self._encoding

    def get_interval(self) -> int:
        """
        代理网站爬取间隔(秒)
        :return:
        """
        return self._interval

    def get_page_range(self) -> Iterable:
        """
        默认只获取第一页内容
        :return:
        """
        return range(1, self._page_limit)

    def get_page_url(self, url: str, page: str):
        """
        拼接 url。子类重写此方法
        :param url:
        :param page:
        :return:
        """
        raise NotImplementedError

    def _judge_type(self, type_str: str):
        """
        判断代理的类型
        :param type_str: 
        :return: 
        """
        type_low = type_str.lower()
        if type_low == 'http':
            return ProxyTypeEnum.HTTP.value
        elif type_low == 'https':
            return ProxyTypeEnum.HTTPS.value
        elif type_low == 'http/https':
            return ProxyTypeEnum.HTTP_AND_HTTPS.value
        else:
            return ProxyTypeEnum.UNKNOWN.value

    def _judge_anonymity(self, cover_str: str):
        """
        判断代理的种类
        :param cover_str: 
        :return: 
        """
        if cover_str == '透明':
            return AnonymityEnum.TRANSPARENT.value
        elif cover_str == '高匿':
            return AnonymityEnum.HIGH_COVER.value
        elif cover_str == '普匿':
            return AnonymityEnum.NORMAL_COVER.value
        else:
            return AnonymityEnum.UNKNOWN.value

    def parse_page(self, resp: str) -> List[ProxyEntity]:
        """
        解析网页内容。子类重写此方法
        :param resp: 返回内容字符串
        :return: 代理列表
        """
        raise NotImplementedError

    def crawl(self):
        """
        开始爬取
        :return:
        """
        res = []
        for url in self._urls:
            for page in self.get_page_range():
                full_url = self.get_page_url(url, page)
                logger.info("抓取 {}".format(full_url))
                resp = requests.get(full_url, verify=False, headers=self._headers)
                while resp.status_code != 200:
                    logger.info("坐下来喝杯茶吧." + full_url)
                    time.sleep(self.get_interval())
                    resp = requests.get(full_url, verify=False, headers=self._headers)
                resp.encoding = self.get_encoding()
                # print(full_url, resp.text)
                temp = self.parse_page(resp.text)
                res.extend(temp)
                time.sleep(self.get_interval())
        return res

    async def crawl_async(self):
        """
        异步爬取
        :return:
        """
        logger.info(f'{self._name}开始爬取...')
        res = []
        for url in self.get_urls():
            try:
                for page in self.get_page_range():
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self.get_page_url(url, page), headers=self._headers) as resp:
                            resp.encoding = self.get_encoding()
                            temp = self.parse_page(await resp.text())
                            res.extend(temp)
                            await asyncio.sleep(self.get_interval())
            except Exception as e:
                logger.exception(f'{self._name}爬取失败url: {url}, :e:{e}')
        return res


############################################################################
#   具体实现类: 已失效
############################################################################

'''
@spider_register
class SpiderQuanWangIp(AbsSpider):
    """
    全网IP代理爬虫 刷新速度:极快。域名出售
    http://www.goubanjia.com/
    """

    def __init__(self) -> None:
        super().__init__('全网IP代理爬虫')
        self._urls = ["http://www.goubanjia.com"]
        self._page_now = 1
        self._page_limit = 7
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        tr_list = soup.find('tbody').find_all('tr')
        for i, tr in enumerate(tr_list):
            tds = tr.find_all('td')
            id_and_port = tds[0]
            ip, port = self._parse_ip_and_port(id_and_port)
            anonymity = tds[1].text
            proxy_type = tds[2].text
            region = tds[3].contents[1].text
            supplier = tds[4].text
            result.append(
                ProxyEntity(
                    f'{proxy_type.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=proxy_type.lower(),
                    source=self._name,
                    supplier=supplier,
                    proxy_type=self._judge_type(proxy_type),
                    anonymity=self._judge_anonymity(anonymity),
                    region=region
                )
            )
        return result

    def _parse_ip_and_port(self, ip_td: Tag):
        res = []
        contents = ip_td.find_all(['div', 'span'])
        for content in contents:
            res.append(content.text)
        res.pop()
        ip = ''.join(res)

        port_tag = contents[-1]
        port_ori_str = port_tag.get('class')[1]
        # 解码真实的端口
        port = 0
        for c in port_ori_str:
            port *= 10
            port += (ord(c) - ord('A'))
        port /= 8
        port = int(port)
        return ip, str(port)


@spider_register
class SpiderFreeProxyLists(AbsSpider):

    def __init__(self) -> None:
        super().__init__('Free Proxy Lists')
        self._urls = ["https://www.freeproxylists.net/zh/"]
        self._page_now = 1
        self._page_limit = 2
        self._page_list = []
        self._interval = 0
        self._headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'www.freeproxylists.net',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0',
        }

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        table = soup.find('table')
        if table is None:
            return []
        print(1111)
        tbody = soup.find('tbody')
        if tbody is None:
            return []
        trs = tbody.find_all('tr')
        for i, tr in enumerate(trs):
            if tr.attrs.get("class") == "Caption":
                continue

            tds = tr.find_all('td')

            if tds[0].attrs.get("colspan") == "10":
                continue

            ip = tds[0].text
            port = tds[1].text
            protocol = tds[2].text
            anonymity = tds[3].text
            # print(ip, port, anonymity, proxy_type, region, supplier)

            result.append(
                ProxyEntity(
                    f'{protocol.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=protocol.lower(),
                    source=self._name,
                    supplier="",
                    proxy_type=self._judge_type(protocol),
                    anonymity=self._judge_anonymity(anonymity),
                    country=tds[4].text,
                    region=tds[5].text,
                    city=tds[6].text,
                    reliability=tds[7].text,
                    response_speed=tds[8].text,
                    transfer_speed=tds[9].text,
                ))
        return result

    def get_page_url(self, url, page) -> str:
        return url + "?page={}".format(page)


@spider_register
class SpiderMianFeiDaiLiIp(AbsSpider):
    """
    免费代理IP库
    http://ip.jiangxianli.com/
    """

    def __init__(self) -> None:
        super().__init__('免费代理IP爬虫')
        self._urls = ["http://ip.jiangxianli.com/"]
        self._page_now = 1
        self._page_limit = 3
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        table = soup.find('table')
        if table is None:
            return []
        tbody = soup.find('tbody')
        if tbody is None:
            return []
        trs = tbody.find_all('tr')
        for i, tr in enumerate(trs):
            if tr.find("div"):
                continue
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[2].text
            proxy_type = tds[3].text if tds[3].text != '' else 'http'
            region = tds[5].text
            supplier = tds[6].text
            result.append(
                ProxyEntity(
                    f'{proxy_type.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=proxy_type.lower(),
                    source=self._name,
                    supplier=supplier,
                    proxy_type=self._judge_type(proxy_type),
                    anonymity=self._judge_anonymity(anonymity),
                    region=region))
        return result

    def get_page_url(self, url, page) -> str:
        return url + "?page={}".format(page)


@spider_register
class SpiderXiciIp(AbsSpider):
    """
    西刺代理爬虫 刷新速度:🐌慢
    基本上没几个代理个能用🆒
    https://www.xicidaili.com/
    """

    def __init__(self) -> None:
        super().__init__('西刺IP代理爬虫')
        self._urls = [
            'https://www.xicidaili.com/nn',  # 高匿
            'https://www.xicidaili.com/nt'  # 透明
        ]
        self._page_now = 1
        self._page_limit = 3
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        tab = soup.find('table', attrs={'id': 'ip_list'})
        if tab is None:
            return []
        tr_list = tab.find_all('tr')[1: -1]
        for tr in tr_list:
            tds = tr.find_all('td')
            ip = tds[1].text
            port = tds[2].text
            anonymity = tds[4].text
            proxy_type = tds[5].text
            result.append(
                ProxyEntity(
                    f'{proxy_type.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=proxy_type.lower(),
                    source=self._name,
                    anonymity=self._judge_anonymity(anonymity),
                    proxy_type=self._judge_type(proxy_type),
                ))
        return result
'''


############################################################################
#   具体实现类: 开始收费
############################################################################

'''
@spider_register
class SpiderIpHaiIp(AbsSpider):
    """
    IP海代理IP 刷新速度: 8分钟/1个。现在开始收费了。
    http://www.iphai.com
    """

    def __init__(self) -> None:
        super().__init__('IP海代理IP爬虫')
        self._urls = [
            'http://www.iphai.com/free/ng',  # 国内高匿
            'http://www.iphai.com/free/np',  # 国内普通
            'http://www.iphai.com/free/wg',  # 国外高匿
            'http://www.iphai.com/free/wp',  # 国外普通
        ]
        self._page_now = 1
        self._page_limit = 6
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        table = soup.find('table')
        if table is None:
            return []
        tbody = soup.find('tbody')
        if tbody is None:
            return []
        trs = tbody.find_all('tr')
        for i, tr in enumerate(trs):
            if i == 0:
                continue
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[2].text
            proxy_type = tds[3].text if tds[3].text != '' else 'http'
            region = tds[4].text
            result.append(
                ProxyEntity(
                    f'{proxy_type.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=proxy_type.lower(),
                    source=self._name,
                    proxy_type=self._judge_type(proxy_type),
                    anonymity=self._judge_anonymity(anonymity),
                    region=region))
        return result

    def get_page_url(self, url, page) -> str:
        return url


@spider_register
class SpiderDieNiao(AbsSpider):
    """
    开始收费了
    """

    def __init__(self) -> None:
        super().__init__('蜂鸟IP爬虫')
        self._urls = ["http://www.dieniao.com/FreeProxy/"]
        self._page_now = 1
        self._page_limit = 9
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'html.parser')
        a = soup.find_all("ul")

        for i, tr in enumerate(a[2].find_all("li")[1:]):
            if tr.find("div"):
                continue
            tds = tr.find_all('span')
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[2].text
            proxy_type = "HTTP"
            region = tds[3].text
            supplier = tds[4].text
            # print(ip, port, anonymity, proxy_type, region, supplier)
            result.append(
                ProxyEntity(
                    url=f'{proxy_type.lower()}://{ip}:{port}',
                    source=self._name,
                    ip=ip,
                    port=port,
                    protocol=proxy_type,
                    supplier=supplier,
                    proxy_type=self._judge_type(proxy_type),
                    anonymity=self._judge_anonymity(anonymity),
                    region=region))
        return result

    def get_page_url(self, url, page) -> str:
        return url + "{}.html".format(page)
'''


############################################################################
#   具体实现类: 存活，但是有反扒措施
############################################################################

@spider_register
class SpiderIHuan(AbsSpider):
    """
    有防爬措施。建议直接在页面查看
    """

    def __init__(self) -> None:
        super().__init__('小幻HTTP代理，有反扒措施')
        self._urls = ["https://ip.ihuan.me/today/2024/01/03/14.html"]
        self._page_now = 1
        self._page_limit = 100
        self._page_list = []
        self._interval = 0
        self._headers = {
            "Cookie": "cf_clearance=jblara61yPHh6v0YcquMhrzw0n5KiBtvV7fxK9H9u28-1704250908-0-2-2885a59a.e8507cd4.7f84fa7a-160.0.0; Hm_lvt_8ccd0ef22095c2eebfe4cd6187dea829=1704250919; statistics=9c1ce27f08b16479d2e17743062b28ed; Hm_lpvt_8ccd0ef22095c2eebfe4cd6187dea829=1704252095",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3",
            "Pragma": "no-cache",
            "Referer": "https://ip.ihuan.me/tqdl.html",
            "Sec-Ch-Ua": """Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120" """,
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def get_page_url(self, url, page) -> str:
        return url + page

    def find_page_list(self, resp):
        soup = BeautifulSoup(resp)
        ul = soup.find_all("ul")
        for i in (ul[2].find_all("a")):
            href = i.attrs.get("href")
            if href and href not in self._page_list:
                self._page_list.append(href)

    def next_page(self, url, reset=False):
        if reset:
            self._page_list = []
            self._page_now = 0
            data = requests.get(url, headers=self._headers)
            print(data)
            print(data.text)
            self.find_page_list(data.text)

        if not self._page_list:
            return False

        if self._page_now > self._page_limit:
            return False
        ret = self._page_list[self._page_now]
        self._page_now += 1
        return ret

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'html.parser')
        table = soup.find("table")
        tbody = table.find("tbody")
        trs = tbody.find_all("tr")

        for i, tr in enumerate(trs):
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text

            anonymity = tds[6].text
            region = tds[2].text
            supplier = tds[3].text

            protocols = ["http", "https"] if tds[4].text == "支持" else ["http"]

            # print(ip, port, anonymity, protocols, region, supplier)
            for protocol in protocols:
                result.append(
                    ProxyEntity(
                        url=f'{protocol.lower()}://{ip}:{port}',
                        source=self._name,
                        ip=ip,
                        port=port,
                        protocol=protocol,
                        supplier=supplier,
                        proxy_type=self._judge_type(protocol),
                        anonymity=self._judge_anonymity(anonymity),
                        region=region))
        return result

    def crawl(self):
        res = []
        for url in self._urls:
            page = self.next_page(url, reset=True)
            while page:
                full_url = self.get_page_url(url, page)
                resp = requests.get(full_url, verify=False, headers=HEADERS)
                while resp.status_code != 200:
                    logger.info("坐下来喝杯茶吧." + full_url)
                    time.sleep(self._interval)
                    resp = requests.get(full_url)
                temp = self.parse_page(resp.text)
                self.find_page_list(resp.text)
                res.extend(temp)
                time.sleep(self.get_interval())
                page = self.next_page(url)
        return res


############################################################################
#   具体实现类: 存活
############################################################################

@spider_register
class Spider66Ip(AbsSpider):
    """
    66IP代理爬虫 刷新速度:🐌慢，现在好像没有代理ip了
    http://www.66ip.cn/
    """

    def __init__(self) -> None:
        super().__init__('66IP代理爬虫，基本上都不能用了')
        self._urls = ['http://www.66ip.cn', ]
        self._page_now = 1
        self._page_limit = 6
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        tr_list = soup.find('table', attrs={'width': '100%', 'bordercolor': '#6699ff'}).find_all('tr')
        for i, tr in enumerate(tr_list):
            if i == 0:
                continue
            contents = tr.contents
            protocol = "http"
            ip = contents[0].text
            port = contents[1].text
            region = contents[2].text
            anonymity = contents[3].text
            result.append(
                ProxyEntity(
                    f'{protocol}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=protocol,
                    source=self._name,
                    anonymity=self._judge_anonymity(anonymity),
                    region=region))
        return result

    def get_page_url(self, url, page) -> str:
        return f'{url}/{page}.html'

    def get_encoding(self) -> str:
        return 'gb2312'

    @staticmethod
    def _judge_anonymity(cover_str: str):
        if cover_str == '高匿代理':
            return AnonymityEnum.HIGH_COVER.value
        else:
            return AnonymityEnum.UNKNOWN.value


@spider_register
class SpiderKuaiDaiLi(AbsSpider):
    """
    快代理IP 刷新速度: 极快
    https://www.kuaidaili.com/free
    """

    def __init__(self) -> None:
        super().__init__('快代理IP代理')
        self._urls = [
            'https://www.kuaidaili.com/free/inha',  # 高匿
            'https://www.kuaidaili.com/free/intr'  # 透明
        ]
        self._page_now = 1
        self._page_limit = 5
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        trs = soup.find('tbody').find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[2].text
            proxy_type = tds[3].text
            region = tds[4].text
            result.append(
                ProxyEntity(
                    f'{proxy_type.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=proxy_type.lower(),
                    source=self._name,
                    proxy_type=self._judge_type(proxy_type),
                    anonymity=self._judge_anonymity(anonymity),
                    region=region))
        return result

    def get_page_url(self, url, page) -> str:
        """
        格式化页数url
        :param url: url
        :param page:
        :return:
        """
        return f'{url}/{page}'


@spider_register
class SpiderKuaiDaiLi1(AbsSpider):
    """
    快代理IP 刷新速度: 极快
    https://www.kuaidaili.com/free
    """

    def __init__(self) -> None:
        super().__init__('快代理IP代理1')
        self._urls = [
            "https://www.kuaidaili.com/ops/proxylist"
        ]
        self._page_now = 1
        self._page_limit = 10
        self._page_list = []
        self._interval = 0

    def _judge_anonymity(self, cover_str: str):
        if cover_str == '透明':
            return AnonymityEnum.TRANSPARENT.value
        elif cover_str == '高匿名':
            return AnonymityEnum.HIGH_COVER.value
        elif cover_str == '普匿':
            return AnonymityEnum.NORMAL_COVER.value
        else:
            return AnonymityEnum.UNKNOWN.value

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        trs = soup.find_all('tbody')[2].find_all('tr')

        for tr in trs:
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[2].text
            proxy_types = tds[3].text
            proxy_types = ["HTTP", "HTTPS"] if proxy_types == "HTTP, HTTPS" else [proxy_types]
            for proxy_type in proxy_types:
                result.append(
                    ProxyEntity(
                        f'{proxy_type.lower()}://{ip}:{port}',
                        ip=ip,
                        port=port,
                        protocol=proxy_type.lower(),
                        source=self._name,
                        proxy_type=self._judge_type(proxy_type),
                        anonymity=self._judge_anonymity(anonymity),
                        region=tds[5].text,
                        response_speed=tds[6].text
                    ))
        return result

    def get_page_url(self, url, page) -> str:
        """
        格式化页数url
        :param url: url
        :param page:
        :return:
        """
        return f'{url}/{page}'


@spider_register
class SpiderYunDaiLiIp(AbsSpider):
    """
    云代理IP 刷新速度: 快
    http://www.ip3366.net/free
    """

    def __init__(self) -> None:
        super().__init__('云代理IP爬虫')
        self._urls = ["http://www.ip3366.net/free/?stype=1", "http://www.ip3366.net/free/?stype=2"]
        self._page_now = 1
        self._page_limit = 5
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        trs = soup.find('table').find('tbody').find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[2].text
            proxy_type = tds[3].text
            region = tds[4].text
            result.append(
                ProxyEntity(
                    f'{proxy_type.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=proxy_type.lower(),
                    source=self._name,
                    proxy_type=self._judge_type(proxy_type),
                    anonymity=self._judge_anonymity(anonymity),
                    region=region))
        return result

    def get_encoding(self) -> str:
        return 'gb2312'

    def get_page_url(self, url, page) -> str:
        return f'{url}&page={page}'


@spider_register
class SpiderKXDaiLi(AbsSpider):
    """
    免费代理IP库
    http://www.kxdaili.com/dailiip/1/1.html
    """

    def __init__(self) -> None:
        super().__init__('开心IP爬虫')
        self._urls = ["http://www.kxdaili.com/dailiip/1/", "http://www.kxdaili.com/dailiip/2/"]
        self._page_now = 1
        self._page_limit = 9
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        table = soup.find('table')
        if table is None:
            return []
        tbody = soup.find('tbody')
        if tbody is None:
            return []
        trs = tbody.find_all('tr')
        for i, tr in enumerate(trs):
            if tr.find("div"):
                continue
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[2].text
            proxy_type = tds[3].text if tds[3].text != '' else 'http'
            region = tds[5].text
            supplier = ""
            # print(ip, port, anonymity, proxy_type, region, supplier)
            proxy_type = ["HTTPS", "HTTP"] if proxy_type == 'HTTP,HTTPS' else [proxy_type]
            for protocol in proxy_type:
                result.append(
                    ProxyEntity(
                        f'{protocol.lower()}://{ip}:{port}',
                        ip=ip,
                        port=port,
                        protocol=protocol.lower(),
                        source=self._name,
                        supplier=supplier,
                        proxy_type=self._judge_type(protocol),
                        anonymity=self._judge_anonymity(anonymity),
                        region=region))
        return result

    def get_page_url(self, url, page) -> str:
        return url + "{}.html".format(page)


@spider_register
class Spider89Ip(AbsSpider):

    def __init__(self) -> None:
        super().__init__('89免费代理')
        self._urls = ["https://www.89ip.cn"]
        self._page_now = 1
        self._page_limit = 2
        self._page_list = []
        self._interval = 0

    def parse_page(self, resp) -> List[ProxyEntity]:
        result = []
        soup = BeautifulSoup(resp, 'lxml')
        table = soup.find('table')
        if table is None:
            return []
        tbody = soup.find('tbody')
        if tbody is None:
            return []
        trs = tbody.find_all('tr')
        for i, tr in enumerate(trs):
            if tr.find("div"):
                continue
            tds = tr.find_all('td')
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            anonymity = ""
            proxy_type = 'http'
            region = tds[2].text.strip()
            supplier = tds[3].text.strip()
            result.append(
                ProxyEntity(
                    f'{proxy_type.lower()}://{ip}:{port}',
                    ip=ip,
                    port=port,
                    protocol=proxy_type.lower(),
                    source=self._name,
                    supplier=supplier,
                    proxy_type=self._judge_type(proxy_type),
                    anonymity=self._judge_anonymity(anonymity),
                    region=region))
        return result

    def get_page_url(self, url, page) -> str:
        return url + "/index_{}.html".format(page)


if __name__ == '__main__':
    result = []
    # obj = SpiderIHuan()
    obj = SpiderKXDaiLi()
    # obj = SpiderYunDaiLiIp()
    # obj = SpiderKuaiDaiLi()
    # obj = Spider66Ip()
    # obj = Spider89Ip()
    # obj = SpiderKuaiDaiLi1()
    temp = obj.crawl()
    for j in temp:
        result.append({
            "proto": j.protocol,
            "ip": j.ip,
            "port": int(j.port),
            "country": j.region,
            "supplier": j.supplier,
            "type": "",
            "anonymity": j.anonymity,
            "source": obj._urls[0],
        })
    print(result)
