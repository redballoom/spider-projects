# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/25
📄File       : n04-CSS伪元素反爬.py
ℹ️Description: 简短描述该文件的主要功能或目的

练习目标：http://www.spiderbuf.cn/n04/
"""

import time

import requests
from lxml import etree


def get_page(url, headers=None, retries=3):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()  # 如果不是200状态码请求，则抛出HTTPError错误
            return response.text
        except requests.exceptions.RequestException as e:  # 通用异常捕获
            print(f"Error making request to {url}: {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(1)  # 重试前等待一段时间
    return None


def parse_page(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html: 网页的源代码数据
    :return: None
    """
    # 在网页中到到伪类的样式表
    pseudo_class = {
        "abcdef::before": "7",
        "abcdef::after": "5",
        "ghijkl::before": "8",
        "ghijkl::after": "9",
        "mnopqr::before": "9",
        "mnopqr::after": "1",
        "uvwxyz::before": "1",
        "uvwxyz::after": "4",
        "yzabcd::before": "2",
        "yzabcd::after": "6",
        "efghij::before": "3",
        "efghij::after": "2",
        "klmnop::before": "5",
        "klmnop::after": "7",
        "qrstuv::before": "4",
        "qrstuv::after": "3",
        "wxyzab::before": "6",
        "wxyzab::after": "0",
        "cdefgh::before": "0",
        "cdefgh::after": "8",
        "hijklm::after": "6",
        "opqrst::after": "0",
        "uvwxab::after": "3",
        "cdijkl::after": "8",
        "pqrmno::after": "1",
        "stuvwx::after": "4",
        "pkenmc::after": "7",
        "tcwdsk::after": "9",
        "mkrtyu::after": "5",
        "umdrtk::after": "2",
    }
    tree = etree.HTML(html)
    title_list = tree.xpath('//div[@class="container"]/div/div/h2/text()')
    scores_list = tree.xpath('//div[@class="container"]/div/div/div[2]/span[2]/@class')
    # 将scores_before和scores_after的值去构建完整的字典的键，然后以键去pseudo_class找对应的值
    for i, item in enumerate(scores_list):
        scores_before = item.split()[0] + '::before'
        scores_after = item.split()[1] + '::after'
        scores = f'{pseudo_class.get(scores_before)}.{pseudo_class.get(scores_after)}'
        print(f'{title_list[i]}: {scores}')


def main():
    page_url = 'http://www.spiderbuf.cn/n04/'
    html_data = get_page(page_url)
    if html_data:
        parse_page(html_data)
    else:
        print(f"Failed to retrieve or parse page: {page_url}")


if __name__ == '__main__':
    main()
