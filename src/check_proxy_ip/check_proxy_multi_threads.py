#!/usr/bin/env python

import codecs
import json
import locale
import optparse
import os
import random
import re
import socket
import subprocess
import sys
import threading
import time
import urllib
import logging

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

# proxy 代理级别：高匿。。。
ANONIMITY_LEVELS = {"high": "elite", "medium": "anonymous", "low": "transparent"}
FALLBACK_METHOD = False

# 获取本机真实ip地址
IFCONFIG_CANDIDATES = (
    "https://api.ipify.org/?format=text",
    "https://myexternalip.com/raw",
    "https://wtfismyip.com/text",
    "https://icanhazip.com/",
    # "https://ipv4bot.whatismyipaddress.com/",
    "https://ip4.seeip.org"
)

# windows 的输出是 nt
IS_WIN = os.name == "nt"

MAX_HELP_OPTION_LENGTH = 18

# 代理ip获取地址
PROXY_LIST_URL = "https://raw.githubusercontent.com/stamparm/aux/master/fetch-some-list.txt"
ROTATION_CHARS = ('/', '-', '\\', '|')
TIMEOUT = 20
THREADS = 20
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"

if not IS_WIN:
    BANNER = re.sub(r"\|(\w)\|", lambda _: "|\033[01;41m%s\033[00;49m|" % _.group(1), BANNER)

options = None
threads = []
timeout = TIMEOUT

SQL_flag = True
if SQL_flag:
    from src.utils.MySQL import MySQLLocal
    from src.utils.ini_util import OPConfig

    opc = OPConfig()
    user = opc.get_config("MySQL", "user")
    port = opc.get_config("MySQL", "port")
    host = opc.get_config("MySQL", "host")
    passwd = opc.get_config("MySQL", "passwd")
    db = opc.get_config("MySQL", "db")


def check_alive(address, port):
    result = False

    try:
        port = int(port)
        s = socket.socket()
        s.connect((address, port))
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


def retrieve(url, data=None, headers={"User-agent": USER_AGENT}, timeout=timeout, opener=None):
    try:
        req = Request("".join(url[i].replace(' ', "%20") if i > url.find('?') else url[i] for i in xrange(len(url))),
                      data, headers)
        retval = (urlopen if not opener else opener.open)(req, timeout=timeout).read()
    except Exception as ex:
        try:
            retval = ex.read() if hasattr(ex, "read") else getattr(ex, "msg", str())
        except:
            retval = None

    return (retval or b"").decode("utf8")


def check(proxy, handle=None):
    start = time.time()
    candidate = "%s://%s:%s" % (proxy["proto"], proxy["ip"], proxy["port"])

    if not all((proxy["ip"], proxy["port"])) or re.search(r"[^:/\w.]", candidate):
        return

    if not check_alive(proxy["ip"], proxy["port"]):
        return

    if not FALLBACK_METHOD:
        print("curl -m %d -A \"%s\" --proxy %s %s" % (timeout, USER_AGENT, candidate, random_ifconfig()))
        process = subprocess.Popen(
            "curl -m %d -A \"%s\" --proxy %s %s" % (timeout, USER_AGENT, candidate, random_ifconfig()),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, _ = process.communicate()
    elif proxy["proto"] in ("http", "https"):
        opener = build_opener(ProxyHandler({"http": candidate, "https": candidate}))
        result = retrieve(random_ifconfig(), timeout=timeout, opener=opener)

    if (result or "").strip() == proxy["ip"].encode("utf8"):
        latency = time.time() - start
        if latency < timeout:
            sys.stdout.write("\r%s%s # latency: %.2f sec; country: %s; anonymity: %s (%s)\n" % (
                candidate, " " * (32 - len(candidate)), latency,
                ' '.join(_.capitalize() for _ in (proxy["country"].lower() or '-').split(' ')), proxy["type"],
                proxy["anonymity"]))
            sys.stdout.flush()
            if handle:
                os.write(handle, ("%s%s" % (candidate, os.linesep)).encode("utf8"))
            return True


def random_ifconfig():
    retval = random.sample(IFCONFIG_CANDIDATES, 1)[0]
    retval = retval.replace("https://", "http://")
    return retval


def check_and_save(queue, handle=None):
    mysql = MySQLLocal(host, port, user, passwd, db)
    try:
        while True:
            proxy = queue.get_nowait()
            # proxy["proto"] = proxy.get("proto").replace("https", "http")
            if SQL_flag:
                sql = "select id from proxy where proto='{}' and  ip='{}' and  port='{}'".format(
                    proxy.get("proto"), proxy.get("ip"), proxy.get("port"))
                if mysql.select(sql):
                    print("数据库中已存在")
                    continue

                if check(proxy, handle):
                    sql = "insert into proxy(proto,ip,port,country,anonymity,type,status,source,supplier) value ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                        proxy.get("proto"), proxy.get("ip"), proxy.get("port"), proxy.get("country"), proxy.get("anonymity"),
                        proxy.get("type"), "1", proxy.get("source"), proxy.get("supplier"))
                    mysql.insert(sql)

    except Exception as e:
        return
        # logging.exception("")



def main(proxy_list):

    if len(proxy_list) == 0:
        print("[!] no proxies found")
        return

    queue = Queue()
    for proxy in proxy_list:
        queue.put(proxy)

    for _ in xrange(THREADS):
        thread = threading.Thread(target=check_and_save, args=[queue,])
        thread.daemon = True

        try:
            thread.start()
        except threading.ThreadError as ex:
            sys.stderr.write("[x] error occurred while starting new thread ('%s')" % ex.message)
            break

        threads.append(thread)

    try:
        alive = True
        while alive:
            alive = False
            for thread in threads:
                if thread.is_alive():
                    alive = True
                    time.sleep(0.1)
    except KeyboardInterrupt:
        sys.stderr.write("\r   \n[!] Ctrl-C pressed\n")
    else:
        sys.stdout.write("\n[i] done\n")
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)


if __name__ == "__main__":
    check_and_save([])
