# -*- coding: utf-8 -*-
import json
import pymongo
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CarPipeline(object):
    
    def __init__(self):
        host = '127.0.0.1'
        port = 27017
        db_name = 'test'
        client = pymongo.MongoClient(host=host,port=port)
        tdb = client[db_name]
        self.port=tdb['car11.21']

    def process_item(self, item, spider):
        text = dict(item)
        self.port.insert(item)
        return item