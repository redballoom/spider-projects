# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : s01-requests库及lxml库入门.py
@ ℹ️Description:

练习目标：http://www.spiderbuf.cn/s01/
"""
# 导入需要的库
import os.path
from lxml import etree

import requests


def get_page(url, headers=None):
    """
    get请求页面
    :param url: 请求链接
    :param headers: 请求头
    :return: 网页源代码数据
    """
    # 提供默认值
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=default_headers, timeout=10)
        response.raise_for_status()  # 如果不是2XX状态码请求，则抛出HTTPError错误
        return response.text
    except requests.exceptions.RequestException as e:  # 通用requests异常捕获
        print(f"Error making request to {url}: {e}")
        return None


def lxml_parse(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html: 网页源代码数据
    :return: None
    """
    dom_tree = etree.HTML(html)
    trs = dom_tree.xpath('/html/body/div/div[1]/table/tbody/tr')  # 如果不熟悉xpath语法，可以直接在控制台元素位置copy
    # 通用方法：先定位到一个个“盒子”，再从“盒子”中遍历取数据。
    for tr in trs:
        index = tr.xpath('./td[1]/text()')[0]
        ip_addr = tr.xpath('./td[2]/text()')[0]
        mac_addr = tr.xpath('./td[3]/text()')[0]
        device_name = tr.xpath('./td[4]/text()')[0]
        device_type = tr.xpath('./td[5]/text()')[0]
        system_name = tr.xpath('./td[6]/text()')[0]
        open_port = tr.xpath('./td[7]/text()')[0] if tr.xpath('./td[7]/text()') else 'None'
        status = tr.xpath('./td[8]/text()')[0]
        file_data = f'{index}|{ip_addr}|{mac_addr}|{device_name}|{device_type}|{system_name}|{open_port}|{status}\n'
        save_data(file_data)


def save_data(data, file_name='s01-设备信息.txt'):
    """数据保存"""
    save_directory = 'datas'
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    path = os.path.join(save_directory, file_name)  # 完整文件路径
    with open(path, mode='a', encoding='utf-8') as f:
        f.write(data)


if __name__ == '__main__':
    page_url = 'http://www.spiderbuf.cn/s01/'
    html_data = get_page(page_url)
    lxml_parse(html_data)
