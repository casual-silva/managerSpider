from scrapy.cmdline import execute

# execute('scrapy crawl amazons'.split()) # 线上已经运行 2020年9月24日 12:45:00
execute('scrapy crawl test_amazons'.split()) # 线上已经运行 2020年9月24日 12:45:00

# category = None, url = None, task_id = None,
# execute("scrapy crawl amazons -a category=Gift & Apparel Boxes -a task_id=789123456 -a url=https://www.amazon.cn/s?bbn=143305071&rh=n%3A116087071%2Cn%3A116169071%2Cn%3A143305071%2Cn%3A164358071&dc&qid=1621221950&rnid=143305071&ref=lp_143305071_nr_n_2".split()) # 线上已经运行 2020年9月24日 12:45:00


