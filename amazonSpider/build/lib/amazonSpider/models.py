# encoding: utf-8

import redis
from peewee import Model, CharField, MySQLDatabase, IntegerField, DecimalField, SmallIntegerField, DateTimeField


conifgs = {
    'mysql_develop': {
        'host': '47.113.99.36',
        'port': 3306,
        'user': 'myt',
        'password': 'Tuling@2020',
        'charset': 'utf8'
    },
    'mysql_produce': {
        'host': '﻿1.14.180.108',
        'port': 3306,
        'user': 'amazon',
        'password': '﻿EI*&(1284kdijk',
        'charset': 'utf8'
    },
    'redis': {
        "host": "127.0.0.1",
        "port": "6379",
        "db": "1",
        "password": ''
    }

}

database = MySQLDatabase('amazon', **conifgs['mysql_develop'])

class RedisDB:

    def __init__(self):
        try:
            self.__pool = redis.ConnectionPool(**conifgs['redis'])  # redis默认端口是6379
            self._redis = redis.Redis(connection_pool=self.__pool)
        except Exception as e:
            input('''
            ****************
                未链接到redis数据库，
                您当前的链接信息为：
                    host = {}
                    port = {}
                    db = {}
                    passwd = {}`
                Exception: {}
            ******************
            '''.format(conifgs['redis']['host'], conifgs['redis']['port'],
                       conifgs['redis']['db'], conifgs['redis']['passwd'], str(e))
                  )

    # 集合操作
    def sadd(self, key, val):
        return self._redis.sadd(key, val)

    def sysmenber(self, key, val):
        return self._redis.sismember(key, val)

    # 连接池自动关闭连接
    def close(self):
        pass

class BaseModel(Model):
    class Meta:
        database = database

class AmaDatas(BaseModel):
    asin = CharField(index=True)
    task_id = CharField(index=True)
    best_sellers_rank = CharField(null=True)
    current_cat_name = CharField(index=True, null=True)
    current_cat_rank = IntegerField(index=True, null=True)
    customer_reviews = CharField(null=True)
    price = CharField(null=True)
    top_cat_name = CharField(index=True, null=True)
    top_cat_rank = IntegerField(index=True, null=True)
    ship_from = CharField(null=True)
    date_first_available = CharField(null=True)
    page = SmallIntegerField(null=True)
    cat_name = CharField(null=True)
    gmt_create = DateTimeField(null=True)
    url = CharField(null=True)
    class Meta:
        table_name = 'ama_datas'

class AmaTasks(BaseModel):
    cat_name = CharField()
    cat_url = CharField()
    job_id = CharField()
    task_id = CharField(primary_key=True)
    status = SmallIntegerField(default=0)
    gmt_create = DateTimeField()
    gmt_modified = DateTimeField()


    class Meta:
        table_name = 'ama_tasks'

class AmaUser(BaseModel):
    password = CharField()
    user_name = CharField()

    class Meta:
        table_name = 'ama_user'
        primary_key = False


class AmaRequestUrl(BaseModel):
    id = IntegerField(primary_key=True)
    cat_name = CharField()
    cat_url = CharField()
    status = SmallIntegerField()
    gmt_modified = DateTimeField()

    class Meta:
        table_name = 'ama_request_url'

if __name__ == '__main__':
    pass
    # data = {'monitor_id': '8', 'monitor_name': '高考',
    #         'monitor_subjects': '郸城', 'monitor_keywords': '高考,一高',
    #         'task_status': '0', 'task_id': 'dakjgsjkd', 'scheduler_id': '7'}
    # # result = SmIcp.select().execute()
    import time
    import datetime
    from amazonSpider.amazonSpider.am_utils import date
    pre_gmt_create = date(time.time() - 86400 * 0.75)
    count = AmaTasks.select().where(AmaTasks.gmt_create >= pre_gmt_create).count()
    print(count)
    # exist = AmaRequestUrl.select().where(AmaRequestUrl.cat_name == '2').limit(1).execute()
    # print(exist[0].cat_url, exist[0].__data__)
    # # db.create_tables([NewsspiderItemCeNewsModel, NewsspiderMonitors,NewsspiderItemCeNewsContentModel, NewsspiderItemSMICPModel, NewsspiderItemCeNewsHtmlContentModel])
