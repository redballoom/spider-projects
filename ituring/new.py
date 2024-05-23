# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/18
📄File       : new_demo.py
ℹ️Description: 简短描述该文件的主要功能或目的

通过搜索获取电子书信息接口 api : https://api.ituring.com.cn/api/Search/Books?q=python&page=1
"""
import logging
from urllib.parse import quote
from typing import List

import requests
import pymongo

SEARCH = '数据库'
# mongodb配置
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = 'ituring_ebook'
COLLECTION_NAME = SEARCH.lower() + '_ebooks'

# 简单配置日志信息, log文件是ERROR,控制台是INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | Line: %(lineno)d | %(message)s')


def get_index_page(page: int):
    """获取page页的接口数据"""
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Host": "api.ituring.com.cn",
        "Referer": "https://www.ituring.com.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    api_url = f"https://api.ituring.com.cn/api/Search/Books?q={quote(SEARCH)}&page={page}"
    try:
        response = requests.get(url=api_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.exception(f"get_index_page an error occurred: {e}")
        return None


def parse_data(json_data: dict):  # 20
    books = []
    try:
        for book in json_data:
            book_id = book.get('id', 0)
            book_name = book.get('name', '')
            cover_img_key = book.get('coverKey', '')
            book_author_name = book.get('authorNameString', '')
            book_price = book.get('bookEditionPrices', '')[0].get('name', '') if book.get('bookEditionPrices', '') else ''
            book_abstract = book.get('abstract', '')
            cover_img = f'https://file.ituring.com.cn/SmallCover/{cover_img_key}'
            dit = {
                'id': book_id,
                'name': book_name,
                'author': book_author_name,
                'price': book_price,
                'abstract': book_abstract,
                'coverImage': cover_img,
            }
            books.append(dit)
        return books
    except Exception as e:
        logging.exception(f"parse_data an error occurred: {e}")
        return None


def save_to_mongo(ebooks: List[dict]):
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    collection.insert_many(ebooks)
    client.close()


# 不推荐使用for循环，因为不知道搜索的数据有多少。
def main():
    page = 1
    while True:
        logging.info(f"Fetching data for {page} page ")
        json_data = get_index_page(page)
        if not json_data:
            logging.info("No more page or failed to fetch data.")
            break
        else:
            books = parse_data(json_data)
            if books:
                save_to_mongo(books)  # 添加一个判断，在没有数据时不进行存储
                logging.info(f"Successfully inserted data for {page} page")
        page += 1


if __name__ == '__main__':
    main()
