from scrapy.cmdline import execute


# execute('scrapy crawl test_amazons'.split()) 
execute("scrapy crawl amazons -a category=Gift & Apparel Boxes -a task_id=789123456 -a url=https://www.amazon.cn/s?bbn=143305071&rh=n%3A116087071%2Cn%3A116169071%2Cn%3A143305071%2Cn%3A164358071&dc&qid=1621221950&rnid=143305071&ref=lp_143305071_nr_n_2".split())


