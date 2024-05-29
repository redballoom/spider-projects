# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/23
📄File       : s07-jax动态加载数据的爬取.py
ℹ️Description: 简短描述该文件的主要功能或目的

练习目标：http://www.spiderbuf.cn/s07/

流程：
    - 1.打开开发者工具，点击网络选项卡，确保打开过滤器，然后点击XHR按钮
    - 2.点击刷新网页，查看加载的数据接口，在预览中如果有数据就是我们要的接口。

特殊的请求头，这就是ajax请求，这个请求头通常被用于标识一个请求是一个AJAX请求。
    X-Requested-With: XMLHttpRequest
"""
# 导入需要的库
import json
import os.path

import requests


def get_page(url, headers=None):
    """
    get请求页面
    :param url: 请求链接
    :param headers: 请求头
    :return: 网页源代码数据
    """
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=default_headers, timeout=10)
        response.encoding = 'utf-8'  # 如果出现乱码就去网页源代码中找charset，它是什么这里的编码就是什么。
        response.raise_for_status()  # 如果不是2XX状态码请求，则抛出HTTPError错误
        # 如果目标网站是ajax接口就可以直接通过json()，返回解析后的python字典数据
        return response.json()
    except requests.exceptions.RequestException as e:  # 通用requests异常捕获
        print(f"Error making request to {url}: {e}")
        return None


def parse(dit_data):
    """
    从字典数据中提取数据
    :param dit_data: 数据接口返回的数据
    :return: page_data_list: 数据列表
    """
    # 字典数据的取值，推荐使用get()方法来取值，因为使用它，在键不存在时也不会报错。
    page_data_list = []
    for data in dit_data:
        dit = {
            'ip': data.get('ip'),
            'mac': data.get('mac'),
            'manufacturer': data.get('manufacturer'),
            'name': data.get('name'),
            'ports': data.get('ports'),
            'status': data.get('status'),
            'type': data.get('type'),
        }
        page_data_list.append(dit)
    return page_data_list


def save_data(data, file_name='s07-设备信息.json'):
    """数据保存"""
    save_directory = 'datas'
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    path = os.path.join(save_directory, file_name)  # 完整文件路径
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    page_url = 'http://www.spiderbuf.cn/iplist/?order=asc'
    # 在爬虫中，如果在请求头中看到以下headers信息，建议都携带上
    my_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
        'Referer': 'http://www.spiderbuf.cn/s07/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    json_data = get_page(page_url, headers=my_headers)
    if json_data:
        data_list = parse(json_data)
        save_data(data_list)
