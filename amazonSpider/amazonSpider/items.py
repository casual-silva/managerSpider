# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonspiderItem(scrapy.Item):
    # define the fields for your item here like:
    asin = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()
    customer_reviews = scrapy.Field()
    date_first_available = scrapy.Field()
    ship_from = scrapy.Field()
    best_sellers_rank = scrapy.Field()
    top_cat_name = scrapy.Field()
    top_cat_rank = scrapy.Field()
    current_cat_name = scrapy.Field()
    current_cat_rank = scrapy.Field()
    page = scrapy.Field()
    gmt_create = scrapy.Field()


