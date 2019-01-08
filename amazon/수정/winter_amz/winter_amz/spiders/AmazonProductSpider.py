# -*- coding: utf-8 -*-
import scrapy
import json 
from winter_amz.items import WinterAmzItem

with open('dataasins.json') as data_file:
    data = json.load(data_file)

class AmazonProductsSpider(scrapy.Spider):
    name = "AmazonItems"
    allowed_domains = ["amazon.com"]
    data_asins = [] # product code list
    for i in range(len(data)):
        data_asins.extend(data[i]["product_data_asin"].split(","))
    for j in range(len(data_asins)):
        data_asins[j] = 'https://www.amazon.com/dp/' + data_asins[j]
    # want to do : start_urls from amazon.com, can't we just extract it from that url?
    # start_urls is initialized in empty form, and the process gets the item code "XXXXXXXXXX"(10digits) from amazon.com

    def start_requests(self):
        for i in range(len(AmazonProductsSpider.data_asins)):
            yield scrapy.Request(AmazonProductsSpider.data_asins[i], self.parse)

    def parse(self, response):
        items = WinterAmzItem()
        cur_url_id = response.request.url.split("/")[-1]
        title = response.xpath('//h1[@id="title"]/span/text()').extract()
        item_exp = response.xpath('//div[@id="feature-bullets"]//li/span[@class="a-list-item"]/text()').extract()
        feature = ",".join(map(lambda x: x.strip(), item_exp)).strip().split(",")
        full_category = response.xpath('//a[@class="a-link-normal a-color-tertiary"]/text()').extract()
        category = "Fashion Hoodies & Sweatshirts"
        image = response.xpath('//img[@id="landingImage"]/@data-old-hires').extract()
        items['id'] = ''.join(cur_url_id).strip()
        items['title'] = ''.join(title).strip()
        items['category'] = ''.join(category).strip()
        items['fullCategory'] = ",".join(map(lambda x: x.strip(), full_category)).strip()
        items['features'] = [] + feature
        items['product_image_url'] = ''.join(image).strip()
        yield items


