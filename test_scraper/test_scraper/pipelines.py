# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import sqlite3
import pymongo

class TestScraperPipeline:
    def process_item(self, item, spider):
        return item

class BooksPipeline:
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    def process_item(self, item, spider):
        item["price"] = float(item["price"].replace("£", ""))

        if "In stock" in item["availability"]:
            item["availability"] = "Disponible"
        else:
            item["availability"] = "Rupture de stock"
        item["rating"] = self.rating_map.get(item["rating"], 0)
        return item

class SQLitePipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect("books.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                title TEXT,
                price REAL,
                availability TEXT,
                rating TEXT
            )
        ''')
        self.connection.commit()

    def process_item(self, item, spider):
        self.cursor.execute('''
            INSERT INTO books (title, price, availability, rating)
            VALUES (?, ?, ?, ?)
        ''', (item["title"], item["price"], item["availability"], item["rating"]))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.connection.close()

class MongoDBPipeline:
    def open_spider(self, spider):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["scrapy_data"]
        self.collection = self.db["books"]

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
