# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import re
import copy
import time
from itemadapter import ItemAdapter

from .am_utils import date
from .models import AmaDatas, AmaTasks
from scrapy.exporters import CsvItemExporter


def filter_datas(data_dict, cat_name):
    __best_sellers_rank = []
    # 处理排名
    for item in data_dict['best_sellers_rank']:
        __rank = re.findall('#([\d,]+)', item[0])
        rank = (__rank[0] if __rank else item[0]).replace(',', '')
        __cat_name = re.sub('See Top \d+ in', '', item[1]).split('(')[0].strip()
        try:
            rank = int(float(rank))
        except:
            rank = 0
        __best_sellers_rank.append([rank, __cat_name])
    # 丢弃无效数据
    if not __best_sellers_rank:
        __best_sellers_rank = [[0, 'No Rank']]
        # raise DropItem('Rank Miss：Can not match Rank >> >> {}'.format(data_dict['url']))
    data_dict['best_sellers_rank'] = __best_sellers_rank
    data_dict['top_cat_rank'] = __best_sellers_rank[0][0]
    data_dict['top_cat_name'] = __best_sellers_rank[0][1]
    data_dict['current_cat_rank'] = __best_sellers_rank[-1][0]
    data_dict['current_cat_name'] = __best_sellers_rank[-1][1]
    if len(__best_sellers_rank) >= 3:
        # 组合大于2可能会有位置错乱的情况， current_cat_name 索引位置不准确
        for item in __best_sellers_rank[::-1]:
            if cat_name == item[1] or cat_name in item[1]:
                data_dict['current_cat_rank'] = item[0]
                data_dict['current_cat_name'] = item[1]
                break
    return data_dict


# 数据存储前处理
class AmazonspiderfilterPipeline:

    def process_item(self, item, spider):
        item = filter_datas(item, spider.cat_name)
        return item

# 数据保存至数据库 Mysql
class AmazonspiderMysqlPipeline:

    def process_item(self, item, spider):
        try:
            info = copy.deepcopy(item._values)
            info['task_id'] = spider.task_id
            info['cat_name'] = spider.cat_name
            AmaDatas.create(**info)
        except Exception as e:
            print(f"管道错误 mysql存储 -> {e}")
        return item

    def close_spider(self, spider):
        # 退出
        print('AmazonspiderMysqlPipeline close_spider >>', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        AmaTasks.update(status=1, gmt_modified=date()).where(AmaTasks.task_id == spider.task_id).execute()

# 导出csv信息
_save_root_path = r"D:\amazon_source_data"
class AmazonspiderCsvPipeline:

    def open_spider(self, spider):
        __save_root_path = os.path.join(_save_root_path, 'amazons_product_{0}.csv')
        file_name_path = __save_root_path.format(spider.task_id)
        self.file = open(file_name_path, 'wb')
        self.csvItemExporter = CsvItemExporter(file=self.file, include_headers_line=True)
        self.csvItemExporter.start_exporting()

    def process_item(self, item, spider):
        del item['best_sellers_rank']
        self.csvItemExporter.export_item(item)
        return item

    def close_spider(self, spider):
        # 退出
        print('AmazonspiderCsvPipeline close_spider >>', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        AmaTasks.update(status=1, gmt_modified=date()).where(AmaTasks.task_id == spider.task_id).execute()
        self.csvItemExporter.finish_exporting()
        self.file.close()


