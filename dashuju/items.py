# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class nhItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    name = scrapy.Field()
    ori_url = scrapy.Field()
    comment = scrapy.Field()
    specs = scrapy.Field()
    area = scrapy.Field()
    address = scrapy.Field()
    sale = scrapy.Field()
    price = scrapy.Field()


class zfItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    name = scrapy.Field()
    ori_url = scrapy.Field()
    rental = scrapy.Field()
    households = scrapy.Field()
    area = scrapy.Field()
    toward = scrapy.Field()
    address = scrapy.Field()
    price = scrapy.Field()


class spItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    name = scrapy.Field()
    big_address = scrapy.Field()
    address = scrapy.Field()
    floor = scrapy.Field()
    area = scrapy.Field()
    price = scrapy.Field()