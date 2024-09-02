# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
import json
import os
from scrapdex.enums.data_type import DType

class ScrapdexPipeline:
    def __init__(self):
        self.data = {
            "number": None,
            "page_url": None,
            'pokemon_name': None,
            "next_evolution": None,
            'height': None,
            'weight': None,
            "type": None,
            "moves": []
        }
        self.index = 0
        self.length = 1

    def process_item(self, item, spider):
        if item["dtype"] == DType.POKEMON:
            self.index = item["index_len"][0]
            if item["index_len"][1] > self.length:
                self.length = item["index_len"][1]
            
            item.pop("index_len")
            item.pop("dtype")
            self.data.update(item)
        elif item["dtype"] == DType.MOVE:
            item.pop("dtype")
            self.data["moves"].append(item)
        
        # return None
            
    def close_spider(self, spider):
        data = {}
        try:
            file = open("data.json", "r")
            data = json.load(file)
            data["data"].append(self.data)
            file.close()
        except:
            data["data"] = [self.data]
        
        with open("index_len.json", "w") as file:
            json.dump({ "index": self.index, "len": self.length }, file)

        file = open("data.json", "w")
        json.dump(data, file, indent=4)
        file.close()