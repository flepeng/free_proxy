# -*- coding:utf-8 -*-
"""
    @Time  : 2024/1/3 17:50
    @Author: lepeng feng
    @File  : test_get_proxy_ip.py
    @Desc  : 
"""
from src.get_proxy_ip.spiders import *
from src.check_proxy_ip.check_proxy import *


def test_base(spider_class):
    result = []
    obj = spider_class()
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
    return result


def test_SpiderIHuan():
    test_base(SpiderIHuan)


def test_SpiderKXDaiLi():
    test_base(SpiderKXDaiLi)


def test_SpiderYunDaiLiIp():
    test_base(SpiderYunDaiLiIp)


def test_SpiderKuaiDaiLi():
    test_base(SpiderKuaiDaiLi)


def test_Spider66Ip():
    test_base(Spider66Ip)


def test_Spider89Ip():
    test_base(Spider89Ip)


def test_SpiderKuaiDaiLi1():
    test_base(SpiderKuaiDaiLi1)

