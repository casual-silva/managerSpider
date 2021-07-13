# encoding: utf-8

import time
import json
import hashlib
import datetime
import requests
from flask import request

try:
    from models import AmaTasks, AmaDatas
except:
    import os
    import sys
    sys.path.insert(0, '..')
    from .models import AmaTasks, AmaDatas


def get_json_param(param_name):
    if request.method == 'POST':
        if request.get_json():
            params = request.get_json()
        elif request.data:
            params = json.loads(request.data.decode('utf8'))
        else:
            params = request.form
    else:
        params = request.args
    if params is None: return None
    if param_name in params.keys():
        return params.get(param_name).strip()
    else:
        return None


# time_str = time.strftime('%Y-%m-%d %H-%M', time.localtime(time.time()))
def date(timestamp=None, format='%Y-%m-%d %H:%M:%S'):
    '''
    时间戳格式化转换日期

    @params
            timestamp ：时间戳，如果为空则显示当前时间
            format : 时间格式

        @return
            返回格式化的时间，默认为 2014-07-30 09:50 这样的形式
        '''
    if not timestamp:
        timestamp = int(time.time())
    if not isinstance(timestamp, int):
        timestamp = int(timestamp)
    d = datetime.datetime.fromtimestamp(timestamp)
    return d.strftime(format)


def make_md5(item):
    '''
    为请求网址与监控方案id产生哈希值
    :param item: url + monitor_id
    :return: hash(md5)
    '''
    fp = hashlib.md5()
    fp.update(item.encode())
    key = fp.hexdigest()
    # `hashlib.sha1().hexdigest()`, is a string.
    return key


def add_task(scheduler_url, scheduler_params, create_time):
    scheduler_result = requests.post(scheduler_url, data=scheduler_params, timeout=5).json()
    jobid = scheduler_result.get('jobid')
    data = {
        'task_id': scheduler_params['task_id'],
        'cat_url': scheduler_params['cat_url'],
        'cat_name': scheduler_params['cat_name'],
        'status': 0,
        'job_id': jobid,
        'gmt_create': create_time
    }
    AmaTasks.insert(data).execute()
    return data

# if __name__ == '__main__':
#     pre_create_time = '2021-05-28 19:26:35'
#     result_num = AmaTasks.select().where(
#         (AmaTasks.gmt_create == "2021-05-28 19:26:35") &
#         (AmaTasks.task_id == "283a74d89ce90ba2209b688cdec5c79a")
#     ).limit(1).exists()
#     print(result_num)
