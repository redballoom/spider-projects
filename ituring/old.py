# -*- coding: utf-8 -*-
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2024年01月03
@ 📄File       : old.py
@ ℹ️Description:


搜索 get: https://api.ituring.com.cn/api/Search/Books?q=python&page=1

"""
import logging

import requests
import pymysql

SEARCH = 'python'
DATABASES_NAME = f'ituring_{SEARCH}_ebooks'
TOTAL_PAGE = 20000  # 选择爬取使用

# 简单配置日志信息
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | Line: %(lineno)d | %(message)s', )

# 配置数据库连接
db_config = {
    'host': '127.0.0.1',
    'port': 3306,  # int
    'user': 'root',
    'password': 'xxxxxxxx',
    'database': 'pyspider',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
connection = pymysql.connect(**db_config)


def get_api(method, url, headers=None, **kwargs):
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    headers = headers or default_headers

    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException() as err:
        logging.info(f"Error making {method} request to {url}: {err}")
        return None


def get_index_pages(search, page):
    page_url = f'https://api.ituring.com.cn/api/Search/Books?q={search}&page={page}'
    logging.info(f'获取当前页面：{page_url}')
    response = get_api('GET', page_url)
    if response:
        data = response.json()
        for info in data:
            book_id = info['id']
            book_name = info['name']
            cover_img_key = info['coverKey']
            book_author_name = info['authorNameString']
            book_price = info['bookEditionPrices'][0]['name']
            book_abstract = info['abstract']

            cover_img = f'https://file.ituring.com.cn/SmallCover/{cover_img_key}'
            # print(book_id, book_name,book_author_name,cover_img, book_price, book_abstract)
            save_to_database(book_id, book_name, book_author_name, cover_img, book_price, book_abstract)
    else:
        logging.info('无响应数据, 请检查url是否正确.')


def recursion_page(search, page=1):
    page_url = f'https://api.ituring.com.cn/api/Search/Books?q={search}&page={page}'
    logging.info(f'获取当前页面：{page_url}')
    response = get_api('GET', page_url)
    if response:
        data = response.json()
        for info in data:
            book_id = info['id']
            book_name = info['name']
            cover_img_key = info['coverKey']
            book_author_name = info['authorNameString']
            book_price = info['bookEditionPrices'][0]['name']
            book_abstract = info['abstract']
            cover_img = f'https://file.ituring.com.cn/SmallCover/{cover_img_key}'
            save_to_database(book_id, book_name, book_author_name, cover_img, book_price, book_abstract)

        try:
            # 递归终止条件，检查数据是否不为空
            if data:
                recursion_page(search, page + 1)
            else:
                return
        except IndexError:
            logging.info('已经到底了...')


def create_table():
    try:
        with connection.cursor() as cursor:
            # 创建表的 SQL 语句
            sql = f"""CREATE TABLE IF NOT EXISTS `{DATABASES_NAME}` (
                        `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        `book_id` SMALLINT UNSIGNED,
                        `book_name` VARCHAR(100) NOT NULL,
                        `book_author_name` VARCHAR(250) NOT NULL,
                        `cover_img` VARCHAR(100),
                        `book_price` SMALLINT UNSIGNED,
                        `book_abstract` TEXT);"""
            cursor.execute(sql)

        # 提交事务
        connection.commit()
        logging.info(f'{DATABASES_NAME} 数据库创建成功')
    except Exception as e:
        # 发生错误时回滚
        logging.info(f"Error creating table: {e}")
        connection.rollback()


def save_to_database(bid, b_name, author_name, cover, price, abstract):
    try:
        with connection.cursor() as cursor:
            # 执行插入数据的 SQL 语句
            sql = F"""INSERT INTO {DATABASES_NAME} (book_id, book_name,book_author_name,cover_img, book_price, book_abstract) 
            VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (bid, b_name, author_name, cover, price, abstract))

        # 提交事务
        connection.commit()
        logging.info("*| Insert to Successful |*")
    except Exception as e:
        # 发生错误时回滚
        logging.info(f"Error saving to database: {e}")
        connection.rollback()


def main():
    # 创建数据库
    create_table()

    # 选择爬取
    # for page in range(1, TOTAL_PAGE + 1):
    #     get_index_pages(SEARCH, page)

    # 递归爬取
    recursion_page(SEARCH)


if __name__ == '__main__':
    main()
