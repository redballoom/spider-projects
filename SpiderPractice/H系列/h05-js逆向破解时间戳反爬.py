# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/27
📄File       : h05-js逆向破解时间戳反爬.py
ℹ️Description: 简短描述该文件的主要功能或目的

http://www.spiderbuf.cn/h05/api/MTcxNjkxMTA1MSw0NDk2ZTgxY2EwNGRkYjYyNjU0NDg0OTkwMWRkNDcyMg==
http://www.spiderbuf.cn/h05/api/MTcxNjkxMTA3OCxjNjE4OTg0ZTY2NGM4NDAxYWFlYzFjMTAwOTk3ZWU2Zg==

var timeStamp = Math[_0xf48905(0x80)](new Date()[_0xf48905(0x71)]() / 0x3e8)
  , _md5 = md5(timeStamp)
  , s = btoa(timeStamp + ',' + _md5);
s的值就是api后面的路径，只需要在python中实现该方法即可

每次刷新都会更新链接
"""
import os
import time
import csv
import hashlib
import base64
from urllib.parse import urljoin

import requests


def get_page(url, headers=None, retries=3):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()  # 如果不是200状态码请求，则抛出HTTPError错误
            return response.json()
        except requests.exceptions.RequestException as e:  # 通用异常捕获
            print(f"Error making request to {url}: {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(2 ** attempt)  # 指数退避策略
    return None


def get_url_path():
    # 获取当前时间戳并转换为字符串
    timestamp = str(int(time.time()))
    # 计算时间戳的MD5哈希值
    timestamp_md5 = hashlib.md5(timestamp.encode('utf-8')).hexdigest()
    # 将时间戳和MD5哈希值以逗号分隔并编码为Base64字符串
    s_result = base64.b64encode(f'{timestamp},{timestamp_md5}'.encode('utf-8')).decode('utf-8')
    print(s_result)
    return s_result


def parse_data(data_list):
    dict_list = []
    for item in data_list:
        dit = {
            'ranking': item['ranking'],
            'password': item['passwd'],
            'cracking_time': item['time_to_crack_it'],
            'use_num': item['used_count'],
        }
        dict_list.append(dit)
    return dict_list


def save_data(datas, file_name='h05-全球最常用密码列表.csv'):
    """数据保存"""
    save_directory = 'datas'
    os.makedirs(save_directory, exist_ok=True)  # exist_ok=True 如果目录已经存在，则不引发错误, False则反之

    fieldnames = ['ranking', 'password', 'cracking_time', 'use_num']
    path = os.path.join(save_directory, file_name)  # 完整文件路径
    file_exists = os.path.exists(path)
    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(datas)


def main():
    base_url = 'http://www.spiderbuf.cn/h05/'
    s = get_url_path()
    api_url = urljoin(base_url, f'api/{s}')

    json_data = get_page(api_url)
    if json_data:
        dict_data = parse_data(json_data)
        save_data(dict_data)


if __name__ == '__main__':
    main()
