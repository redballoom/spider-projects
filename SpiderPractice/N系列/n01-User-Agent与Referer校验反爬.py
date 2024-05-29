# -*- coding: utf-8 -*-
"""
@Author     : 🎈
@Time       : 2023-12-30
@File       : n01-User-Agent与Referer校验反爬.py
@Description:
练习目标：http://www.spiderbuf.cn/n01/

这里最开始我们是使用默认的UA，请求发现报错403 Client Error，这就是防盗链反爬了，
在headers中添加referer参数即可。
"""
# 导入需要的库
import os
import csv

import requests
from lxml import etree

save_directory = 'datas'
os.makedirs(save_directory, exist_ok=True)  # exist_ok=True 如果目录已经存在，则不引发错误, False则反之


def get_page(url, headers=None, retries=3):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    for _ in range(retries):
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()  # 如果不是200状态码请求，则抛出HTTPError错误
            return response.text
        except requests.exceptions.RequestException as e:  # 通用异常捕获
            print(f"Error making request to {url}: {e}")
    return None


def lxml_parse(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html: 一页的网页源代码数据
    :return data: 解析后的一页字典数据列表
    """
    data = []
    dom_tree = etree.HTML(html)
    divs = dom_tree.xpath('//div[@class="container"]/div/div')
    for div in divs:
        title = div.xpath('./h2/text()')[0]
        ranking = div.xpath('./p[1]/text()')[0].replace('排名：', '')
        value = div.xpath('./p[2]/text()')[0].replace('企业估值(亿元)：', '')
        ceo_name = div.xpath('./p[3]/text()')[0].replace('CEO：', '')
        profession = div.xpath('./p[4]/text()')[0].replace('行业：', '')
        dic = {'企业': title,
               '排名': ranking,
               '企业估值(亿元)': value,
               'CEO': ceo_name,
               '行业': profession
               }
        data.append(dic)
    return data


def save_data(datas, file_name='n01胡润中国500强.csv'):
    """数据保存"""
    fieldnames = ['企业', '排名', '企业估值(亿元)', 'CEO', '行业']
    path = os.path.join(save_directory, file_name)

    with open(path, 'w', newline='', encoding='utf-8') as w_f:
        writer = csv.DictWriter(w_f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(datas)


def main():
    url = 'http://www.spiderbuf.cn/n01/'
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
        'Referer': 'http://www.spiderbuf.cn/list'
    }
    html_data = get_page(url, headers=my_headers)
    if html_data:
        data_list = lxml_parse(html_data)
        save_data(data_list)
    print('All Done!')


if __name__ == '__main__':
    main()
