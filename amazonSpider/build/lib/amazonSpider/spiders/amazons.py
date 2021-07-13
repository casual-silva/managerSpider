# coding:utf-8

import re
import time
import scrapy

from ..items import AmazonspiderItem

# 特殊格式   s?k = not in response.url
# https://www.amazon.com/b?node=689637011&ref=lp_172623_nr_n_11


class CatAmazonSpider(scrapy.Spider):
    name = 'amazons'
    page_count = 100
    allowed_domains = ['amazon.com']
    # cate_name = 'Gift & Apparel Boxes'
    # start_urls = ['https://www.amazon.com/s?k=Tool+Sets&i=tools&rh=n%3A228013%2Cn%3A328182011%2Cn%3A551238%2Cn%3A553402&dc&qid=1621260310&rnid=228013&ref=sr_nr_n_3']

    def __init__(self, cate_name=None, cat_url=None, task_id=None, create_time=None, *args, **kwargs):
        super(CatAmazonSpider, self).__init__(*args, **kwargs) # <- important
        self.cate_name = cate_name
        print("Crawl Paramas: ", cat_url, cate_name, task_id, create_time)
        self.start_urls = [cat_url]
        self.task_id = task_id
        self.create_time = create_time

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # 测试详情页
        # self.parse_detail(response)
        # return
        # return self.parse_detail(response)
        # 检查是否被检测
        with open('/home/amazon_source_data/{}.html'.format(self.task_id), 'wb') as fp:
            fp.write(response.body)
        all_result_href = response.xpath('//div[@class="a-box-inner"]//a[@class="a-link-normal"]/@href').get()
        # 解析首页列表数据
        product_list = response.xpath('//span[@data-component-type="s-product-image"]/a/@href').getall()
        for url in product_list:
            # break
            yield response.follow(url, callback=self.parse_detail, meta={'page': 1})
        # 判断是否显示全部结果
        if all_result_href:
            yield response.follow(all_result_href)
        else:
            curent_url = response.url
            if re.findall('s\?\w=', response.url):
                __curent_url = response.xpath('//ul[@class="a-pagination"]//li[@class="a-last"]/a/@href').get()
                curent_url = response.urljoin(__curent_url)
            # 直接分页
            __page_count = response.css('.a-padding-base li:nth-last-child(2) ::text').get()
            if __page_count:
                # 最多抓取100页
                page_count = 50 if int(__page_count.strip()) > 50 else int(__page_count.strip())
                for num in range(2, page_count+1)[::-1]:
                    if '&page=' not in curent_url:
                        url = curent_url + '&page={}'.format(num)
                    else:
                        url = re.sub('&page=\d+', '&page={}'.format(num), curent_url)
                    yield response.follow(url, callback=self.get_product_list,
                                          meta={'page_count': page_count, 'num': num})
                    # break

    def get_product_list(self, response):
        product_list = response.xpath('//span[@data-component-type="s-product-image"]/a/@href').getall()
        for url in product_list:
            yield response.follow(url, callback=self.parse_detail, meta={'page': response.meta['num']})
            # break


        # # 上一轮翻页结束判断是否需要继续翻页
        if response.meta['page_count'] == response.meta['num']:
            if not response.css('.a-padding-base li:nth-last-child(2) ::text'):
                return
            page_count = int(''.join(response.css('.a-padding-base li:nth-last-child(2) ::text').getall()).strip().replace('\n', ''))
            if page_count > response.meta['page_count']:
                # 继续翻页
                for num in range(response.meta['page_count']+1, page_count + 1)[::-1]:
                    url = re.sub('&page=\d+', '&page={}'.format(num), response.url)
                    yield response.follow(url, callback=self.get_product_list,
                                              meta={'page_count': page_count, 'num': num})

    def parse_detail(self, response):
        result_dict = AmazonspiderItem()
        result_dict['best_sellers_rank'] = []
        result_dict['url'] = response.url
        result_dict['page'] = response.meta['page']
        result_dict['price'] = response.css('.priceBlockBuyingPriceString::text').get()
        result_dict['gmt_create'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 发货地址
        __ship_from = response.xpath('//table[@id="tabular-buybox-container"]/tr')
        if __ship_from:
            ship_from = __ship_from[0].css('td:nth-child(2) span span::text').get()
        else:
            ship_from = 'Unknow'
        result_dict['ship_from'] = ship_from
        # 定位所需数据集中位置
        k_v_table = response.css('#productDetails_detailBullets_sections1 tr')
        k_v_line = response.xpath('//div[@id="detailBulletsWrapper_feature_div"]/ul/li/span | //div[@id="detailBulletsWrapper_feature_div"]/div/ul/li/span')
        # 销售排名格式判断 +1 ﻿id="SalesRank"
        k_v_line_sale = response.xpath('//div[@id="detailBulletsWrapper_feature_div"]//li/ul/li')
        # 表格形式数据
        if k_v_table:
            for tr in k_v_table:
                th_name = tr.xpath('./th/text()').get()
                if not th_name:
                    continue
                th_name = th_name.strip()
                if 'ASIN' == th_name:
                    result_dict['asin'] = tr.xpath('./td/text()').get().strip()
                elif 'Customer Reviews' == th_name:
                    __stars = tr.xpath('./td/text()').getall()
                    stars = ''.join(__stars).strip()
                    ratings = tr.xpath('./td//span[@id="acrCustomerReviewText"]/text()').get().strip()
                    result_dict['customer_reviews'] = stars + ' | ' + ratings
                elif 'Best Sellers Rank' == th_name:
                    spans = tr.xpath('./td/span/span')
                    for span in spans:
                        rank = span.xpath('./text()').get().strip()
                        cat_name = span.xpath('./a/text()').get().strip()
                        result_dict['best_sellers_rank'].append((rank, cat_name))
                elif 'Date First Available' == th_name:
                    result_dict['date_first_available'] = tr.xpath('./td/text()').get().strip()

        elif k_v_line:
            if k_v_line_sale:
                top_cat = response.xpath('//div[@id="detailBulletsWrapper_feature_div"]//div/li/text()').getall()
                if top_cat:
                    __top_cat_name = response.xpath('//div[@id="detailBulletsWrapper_feature_div"]//div/li/a/text()').get()
                    __top_cat_rank = ''.join(top_cat)
                    result_dict['best_sellers_rank'].append((__top_cat_rank, __top_cat_name))
                for li in k_v_line_sale:
                    __span = li.xpath('./span')
                    __rank = __span[0].xpath('./text()').get().strip()
                    __name = __span[1].xpath('./a/text()').get().strip()
                    result_dict['best_sellers_rank'].append((__rank, __name))

            for span in k_v_line:
                span_name = span.css('.a-text-bold::text').get()
                if not span_name:
                    continue
                span_name = span_name.strip()

                if 'ASIN' in span_name:
                    result_dict['asin'] = span.css('span:nth-child(2)::text').get().strip()

                elif 'Best Sellers Rank:' == span_name:
                    rank = ''.join(span.xpath('./text()').getall()).strip()
                    name = span.xpath('./a/text()').get().strip()
                    result_dict['best_sellers_rank'].append((rank, name))
                    for span in span.xpath('./ul/li/span'):
                        rank = span.xpath('./text()').get().strip()
                        name = span.xpath('./a/text()').get().strip()
                        result_dict['best_sellers_rank'].append((rank, name))
                elif 'Customer Reviews' in span_name:
                    stars = span.xpath('.//a/i/span/text()').get().strip()
                    ratings = span.css('#acrCustomerReviewText::text').get().strip()
                    result_dict['customer_reviews'] = stars + ' | ' + ratings
                elif 'Date First Available' in span_name:
                    result_dict['date_first_available'] = span.css('span:nth-child(2)::text').get().strip()
        else:
            raise Exception('Parse_Detail_Error: 详情页面格式异常 >> {}'.format(response.url))
        yield result_dict
