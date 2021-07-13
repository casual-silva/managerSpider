# encoding: utf-8

import os
import sys
import time
import hashlib
import traceback
from functools import wraps
from flask import Flask, request, jsonify, session, make_response
from models import AmaTasks, AmaRequestUrl
from am_utils import date, add_task, get_json_param


sys.path.append('..')

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)

status_code = {
    '0': '成功',
    "400": '参数错误',
    '403': "禁止提交",
    '500': '服务端异常',
}

port = '8081'
host = '0.0.0.0'
BASE_URL = 'http://127.0.0.1:6800/'


def auth_verify(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) # 弃用验证
    return wrapper


@app.route('/api/task/add', methods=['POST'])
@auth_verify
def add():
    cat_name = get_json_param("cat_name")
    cat_url = get_json_param("cat_url")
    if not cat_name:
        return jsonify({'code': '400', 'msg': 'add paramas error', 'data': None})
    # 生成task_id
    gmt_create = date()
    task_id = hashlib.md5((cat_name + '@' + gmt_create).encode('utf8')).hexdigest()

    # 判断当前任务一天内是否重复存在
    pre_gmt_create = date(time.time() - 86400 * 0.8)
    exist = AmaTasks.select().where(
        (AmaTasks.gmt_create >= pre_gmt_create) &
        (AmaTasks.cat_name == cat_name)
    ).limit(1).exists()
    if exist:
        return jsonify({'code': '403', 'msg': '禁止相同分类任务一天内重复提交', 'data': None})

    # 判断每5小时提交上限 5个小时内不超过3个
    pre_gmt_create = date(time.time() - 3600 * 5)
    count = AmaTasks.select().where(AmaTasks.gmt_create >= pre_gmt_create).count()
    if count >= 3:
        return jsonify({'code': '403', 'msg': '5个小时内不超过3个任务', 'data': None})

    # 判断每日提交上限 18个小时内不超过5个
    pre_gmt_create = date(time.time() - 86400 * 0.8)
    count = AmaTasks.select().where(AmaTasks.gmt_create >= pre_gmt_create).count()
    if count >= 5:
        return jsonify({'code': '403', 'msg': '当天任务提交已达到 5个 上限', 'data': None})
    #　分类名判断　｜　及获取cat_url
    cat_result = AmaRequestUrl.select(AmaRequestUrl.cat_url).where(AmaRequestUrl.cat_name == cat_name).limit(1).execute()
    if not list(cat_result):
        return jsonify({'code': '403', 'msg': '不允许提交未经验证的的分类名', 'data': None})

    # Add Task
    scheduler_url = BASE_URL + 'schedule.json'
    scheduler_params = {
        'project': 'amazonSpider',
        'spider': 'amazons',
        'task_id': task_id,
        'cat_name': cat_name,
        'cat_url': cat_result[0].cat_url,
    }
    try:
        # Scheduling and save task
        print('scrapyd paramas: >> ', scheduler_params)
        result = add_task(scheduler_url, scheduler_params, gmt_create)
    except Exception as e:
        print('error:', traceback.print_exc())
        return jsonify({'code': '500', 'msg': 'add api exception: {}, please try again'.format(str(e)), 'data': None})
    return jsonify({'code': '0', 'msg': 'success', 'data': result})


@app.route('/api/cat/verify', methods=['GET'])
@auth_verify
def cat_select():
    # 返回允许抓取的分类信息
    cat_name = get_json_param('cat_name')
    #　判断分类名是否存在
    exist = AmaRequestUrl.select().where(AmaRequestUrl.cat_name == cat_name).limit(1).execute()
    if list(exist):
        return jsonify({'code': '0', 'msg': 'success', 'data': exist[0].__data__})
    else:
        return jsonify({'code': '0', 'msg': 'success', 'data': None})
# ---------------------以下是弃用接口------------------------------

@app.route('/api/task/search/disable', methods=['GET'])
@auth_verify
def search():
    page = int(get_json_param('page')) if get_json_param('page') else 1
    __number = int(get_json_param('number')) if get_json_param('number') else 10
    number = 50 if __number > 50 else __number  # number 最多十条
    cat_name = get_json_param('cat_name')
    if cat_name:
        # 单一查询
        results = AmaTasks.select().where(AmaTasks.cat_name == cat_name).limit(10).execute()
    else:
        # 首页展示
        results = AmaTasks.select().order_by(AmaTasks.gmt_create.desc()).paginate(page, number)
    result = [item.__data__ for item in results]
    return jsonify({'code': '100', 'msg': 'search parameter error', 'data': result})


if __name__ == '__main__':
    app.run(host, port, debug=True)
