# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import sqlite3
import pymongo
import csv


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

class CSVPipeline:
    def open_spider(self, spider):
        self.file = open("books.csv", "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file, quoting=csv.QUOTE_MINIMAL)
        self.writer.writerow(["title", "price", "availability", "rating"])

    def process_item(self, item, spider):
        self.writer.writerow([
            item["title"],
            item["price"],
            item["availability"],
            item["rating"]
        ])
        return item

    def close_spider(self, spider):
        self.file.close()
class JSONPipeline:
    def open_spider(self, spider):
        self.file = open("books.json", "w")
        self.file.write("[\n")

    def process_item(self, item, spider):
        self.file.write(f"{dict(item)},\n")
        return item

    def close_spider(self, spider):
        self.file.write("]\n")
        self.file.close()

class XMLPipeline:
    def open_spider(self, spider):
        self.file = open("books.xml", "w")
        self.file.write("<books>\n")

    def process_item(self, item, spider):
        self.file.write(f"  <book>\n")
        for key, value in item.items():
            self.file.write(f"    <{key}>{value}</{key}>\n")
        self.file.write(f"  </book>\n")
        return item

    def close_spider(self, spider):
        self.file.write("</books>\n")
        self.file.close()

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
        self.db = self.client["books_db_one"]
        self.collection = self.db["books"]

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()