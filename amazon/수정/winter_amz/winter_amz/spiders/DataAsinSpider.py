# -*- coding: utf-8 -*-
import scrapy
from winter_amz.items import DataAsin

class DataAsinSpider(scrapy.Spider):
    name = "DataAsins"
    allowed_domains = ["amazon.com"]
    # start_urls dynamic with range(1,n). page number will be decided by n. 
    start_urls = ("https://www.amazon.com/s/ref=sr_pg_2?fst=as%3Aoff&rh=n%3A16225018011%2Cn%3A1040660%2Cn%3A1258603011&page={}&bbn=16225018011&ie=UTF8&qid=1545919425&ajr=3".format(i) for i in range(1,195))

    def parse(self, response):
        items = DataAsin()
        data_asin = response.css('li').xpath('@data-asin').extract()
        items['product_data_asin'] = ",".join(data_asin).strip()
        yield items
