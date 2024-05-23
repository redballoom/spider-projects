# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/18
📄File       : new.py
ℹ️Description: 抓取当当网电子书书籍信息并保存至mongodb数据库中

"""
import requests
from pymongo import MongoClient, ASCENDING
from loguru import logger

# 抓取配置
TOTAL_PAGES = 10
SEARCH_CATEGORY = 'WX'
API_URL = 'https://e.dangdang.com/media/api.go'
# mongodb配置
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = 'dangdang_ebook'

# 设置文件日志记录
logger.add('dangdang.log', mode='a', level='INFO', retention="1 days", encoding="utf-8")


def get_api(url, params=None):
    """发送GET请求并返回JSON响应"""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return None


def generate_page():
    """生成TOTAL_PAGES页数的翻页参数生成器"""
    for page_num in range(TOTAL_PAGES):
        start_index = page_num * 20 + page_num
        end_index = start_index + 20
        yield start_index, end_index


def generate_api_params(start, end):
    """生成API请求的参数"""
    return {
        'action': 'mediaCategoryLeaf',
        'promotionType': '1',
        'deviceSerialNo': 'html5',
        'macAddr': 'html5',
        'channelType': 'html5',
        'permanentId': '20240518003130451427106758993813485',
        'returnType': 'json',
        'channelId': '70000',
        'clientVersionNo': '6.8.0',
        'platformSource': 'DDDS-P',
        'fromPlatform': '106',
        'deviceType': 'pconline',
        'token': '',
        'start': start,
        'end': end,
        'category': SEARCH_CATEGORY,
        'dimension': 'comment',
        'order': '0'
    }


def parse_data(json_data):
    """解析API返回的JSON数据"""
    data_list = json_data.get('data', {}).get('saleList', [])
    ebooks = []
    for data in data_list:
        media = data.get('mediaList', [])[0] if data.get('mediaList') else {}
        ebook_dict = {
            'title': media.get('title', ''),
            'author': media.get('authorPenname', ''),
            'price': media.get('salePrice', 0),
            'category': media.get('categorys', []),
            'descs': media.get('descs', ''),
            'recommend': media.get('editorRecommend', ''),
        }
        ebooks.append(ebook_dict)
    return ebooks


def save_to_mongodb(ebooks, collection):
    """将解析后的书籍数据保存到MongoDB"""
    if ebooks:
        try:
            result = collection.insert_many(ebooks)
            logger.info(f'Successfully inserted {len(result.inserted_ids)} ebooks')
        except Exception as e:
            logger.error(f"Failed to save to MongoDB: {e}")


def main():
    """主函数，执行爬取和存储流程"""
    collection_name = SEARCH_CATEGORY.lower() + '_ebooks'
    with MongoClient(MONGO_URI) as client:
        db = client[DB_NAME]
        collection = db[collection_name]
        if collection_name not in db.list_collection_names():
            collection.create_index([('title', ASCENDING)], unique=False)
            logger.info(f"Collection '{collection_name}' created with index on 'title'")
        else:
            logger.info(f"Collection '{collection_name}' already exists")

        for start, end in generate_page():
            params = generate_api_params(start, end)
            json_data = get_api(API_URL, params=params)
            if json_data:
                ebooks = parse_data(json_data)
                save_to_mongodb(ebooks, collection)


if __name__ == '__main__':
    main()
