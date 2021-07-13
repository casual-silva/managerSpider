# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import re
import logging
import random
import time
import threading
import requests
from scrapy import signals
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from twisted.internet.error import ConnectionRefusedError, TimeoutError

lock = threading.Lock()
proxy_list = []
expire_time = 10
curent_time = time.time()
bind_api = 'http://www.zdopen.com/ExclusiveProxy/BindIP/?api=202106091655498977&akey=0efee6db315eaa0b&i=1'
proxy_api = 'http://www.zdopen.com/ExclusiveProxy/GetIP/?api=202106091655498977&akey=0efee6db315eaa0b&count=6&pro=1&order=1&type=3'

def get_proxies():

    def get_web_proxy():
        __list = []
        rsp = requests.get(proxy_api).json()
        for item in rsp['data']['proxy_list']:
            ip_port = "https://{0}:{1}".format(item['ip'], item['port'])
            __list.append(ip_port)
        return __list

    global proxy_list
    global curent_time
    if not proxy_list or time.time() - curent_time > expire_time:
        lock.acquire()
        try:
            proxy_list = get_web_proxy()
        except:
            try:
                time.sleep(1)
                proxy_list = get_web_proxy()
            except Exception as e:
                lock.release()
                print('获取代理出错：{}'.format(e))
                return None
        lock.release()
        curent_time = time.time()
        return random.choice(proxy_list)
    else:
        return random.choice(proxy_list)


class MyRetryMiddleware(RetryMiddleware):
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.bind_ip()

    def bind_ip(self):
        rsp = requests.get(bind_api).json()
        self.logger.warning(rsp)

    def _delete_proxy(self, proxy=None):
        if proxy in proxy_list:
            proxy_list.remove(proxy)

    def process_request(self, request, spider):
        proxy = get_proxies()
        self.logger.warning('request.url: {0} 使用代理：{1}'.format(request.url, proxy))
        request.meta["proxy"] = proxy


    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除该代理
            self._delete_proxy(request.meta.get('proxy', False))
            self.logger.warning('返回值异常, 进行重试...')
            return self._retry(request, reason, spider) or response
        return response


    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            # 删除该代理
            self._delete_proxy(request.meta.get('proxy', False))
            self.logger.warning('连接异常: {} ; 进行重试...'.format(str(exception)))
            return self._retry(request, exception, spider)
