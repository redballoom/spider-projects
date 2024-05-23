# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/16
📄File       : 52pj.py
ℹ️Description: 采集52pj网的淘贴的所有专辑数据信息并保存至csv文件
此代码中大量采用GPT给出的优化建议，所以你会看到很多没使用过的方法，这是正常的，学习就完了。
"""

import random
import time
import re
import types
from urllib.parse import urljoin
import csv
import urllib3

from loguru import logger
import requests
from lxml import etree
from requests.utils import get_encoding_from_headers

base_url = 'https://www.52pojie.cn/'

# 提前写入头部信息，避免在后续调用时多次写入
fieldnames = ['album_title', 'album_url', 'album_rss', 'album_review', 'album_author', 'album_latest_time']
with open('data1.csv', 'w', newline='', encoding='utf-8') as w_file:
    writer_header = csv.DictWriter(w_file, fieldnames=fieldnames)
    writer_header.writeheader()

# 禁止显示InsecureRequestWarning警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_page(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        # 使用 response.apparent_encoding 可能更保险，当没有明确charset时
        response.encoding = (
            requests.utils.get_encoding_from_headers(response.headers)
            if 'charset' in response.headers.get('content-type', '').lower()
            else response.apparent_encoding
        )
        return response.text
    except requests.exceptions.Timeout as e:
        logger.exception(f"请求超时错误 {url}: {e}")
        raise  # 向上层抛出异常，不在这里处理
    except requests.exceptions.RequestException as e:
        logger.exception(f"请求错误 {url}: {e}")
        raise  # 向上层抛出异常


def get_index_page(page):
    """
    获取52pojie.cn论坛收藏页的HTML数据并进行解析。

    参数:
    page (int): 需要抓取的收藏页数

    返回:
    - 如果解析成功，返回解析后的数据。
    - 如果请求失败或解析失败，返回相应的错误信息。
    - 如果在获取或解析过程中遇到异常，返回异常错误信息。
    """
    page_url = f'https://www.52pojie.cn/forum.php?mod=collection&order=dateline&op=all&page={page}'
    try:
        html_data = get_page(page_url)
        # 检查请求是否成功
        if html_data:
            # 随机延迟后进行解析
            cho = [0.5, 0.8, 1, 1.2, 1.5, 1.8, 2, 2.5]
            time.sleep(random.choice(cho))
            logger.info(f'......开始解析第{page}页......')
            parsed_data = parse(html_data)
            # 检查解析是否成功
            if parsed_data:
                return parsed_data
            else:
                logger.error("解析失败，未获取到有效数据")
                return "解析错误"
        else:
            logger.error(f"请求第{page}页失败，未获取到HTML数据")
            return "请求错误"
    except Exception as e:
        logger.exception(f"在获取或解析第{page}页时出现错误: {e}")
        return "异常错误"


def parse(html):
    """
    解析HTML数据，提取专辑信息。

    参数:
    html (str): HTML数据
    base_url (str): 基础URL，用于构建绝对URL

    返回:
    - 如果解析成功，返回包含专辑信息的字典列表。
    - 如果解析失败，返回错误信息。
    """
    try:
        tree = etree.HTML(html)
        divs = tree.xpath('//div[contains(@class, "clct_list")]/div')
        for item in divs:
            album_title = item.xpath('./dl/dt/div/a/text()')[0]
            album_path = item.xpath('./dl/dt/div/a/@href')[0]
            album_url = urljoin(base_url, album_path)
            album_info = item.xpath('./dl/dd[2]/p[2]/text()')[0]
            album_rss = re.search(r'订阅 (\d+)', album_info).group(1) if re.search(r'订阅 (\d+)', album_info) else ''  # 订阅
            album_review = re.search(r'评论 (\d+)', album_info).group(1) if re.search(r'评论 (\d+)', album_info) else ''  # 评论
            album_author = item.xpath('./dl/dd[2]/p[3]/a/text()')[0]
            album_update_time = item.xpath('./dl/dd[2]/p[3]/text()')[0]
            album_latest_time = re.sub('创建, 最后更新', '', album_update_time)

            dit = {
                'album_title': album_title,  # 专辑标题
                'album_url': album_url,  # 专辑链接
                'album_rss': album_rss,  # 专辑订阅
                'album_review': album_review,  # 专辑评论
                'album_author': album_author,  # 专辑作者
                'album_latest_time': album_latest_time,  # 专辑最新时间
            }
            yield dit
    except IndexError as e:
        logger.error(f"解析失败，未获取到有效数据: {e}")
        yield "解析错误"
    except Exception as e:
        logger.exception(f"在解析HTML时出现错误: {e}")
        yield "解析错误"


def save_to_csv(data):
    """
    将接收的数据保存为csv文件
    :param data: 接收一个生成器对象
    :return:
    """
    with open('data.csv', 'a', newline='', encoding='utf-8') as a_file:
        writer = csv.DictWriter(a_file, fieldnames=fieldnames)
        for row in data:
            writer.writerow(row)


def main():
    for i in range(1, 3):
        gen_page_data = get_index_page(i)
        if isinstance(gen_page_data, types.GeneratorType):  # 只要正确返回值才处理
            save_to_csv(gen_page_data)
            logger.info(f'保存第{i}页数据完毕')


if __name__ == '__main__':
    main()
