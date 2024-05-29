# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/23
📄File       : s05-网页图片的爬取及本地保存.py
ℹ️Description: 简短描述该文件的主要功能或目的

练习目标：http://www.spiderbuf.cn/s05/
"""
# 导入需要的库
from urllib.parse import urljoin
import os.path
import requests
from lxml import etree


def get_page(url, headers=None):
    """
    通用get请求页面，直接返回对象方便函数复用
    :param url: 请求链接
    :param headers: 请求头
    :return: response 响应对象
    """
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=default_headers, timeout=10)
        response.raise_for_status()  # 如果不是2XX状态码请求，则抛出HTTPError错误
        return response
    except requests.exceptions.RequestException as e:  # 通用requests异常捕获
        print(f"Error making request to {url}: {e}")
        return None


def lxml_parse(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html: 网页源代码数据
    :return: 包装img_url的生成器
    """
    dom_tree = etree.HTML(html)
    img_url_list = dom_tree.xpath('//div[@class="table-responsive"]/div/img/@src')  # 如果不熟悉xpath语法，可以直接在控制台元素位置copy
    for img_link in img_url_list:
        img_link = urljoin('http://www.spiderbuf.cn/', img_link)
        yield img_link


def save_data(file_name, data):
    """图片数据保存"""
    save_directory = 'datas/s05图片保存'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    path = os.path.join(save_directory, f'{file_name}.jpg')  # 完整文件路径
    # 保存图片、音频、视频等二进制数据时 mode='wb'，这是固定的，表示二进制写入模式。同时也不能进行encoding编码。
    with open(path, mode='wb') as f:
        f.write(data.content)  # 保存二进制数据要使用content其类型是bytes，注意它是属性的调用


if __name__ == '__main__':
    page_url = 'http://www.spiderbuf.cn/s05/'
    html_data = get_page(page_url).text
    if html_data:
        gen_img = lxml_parse(html_data)
        for img_name, img_url in enumerate(gen_img):
            img_content = get_page(img_url)
            save_data(img_name, img_content)
