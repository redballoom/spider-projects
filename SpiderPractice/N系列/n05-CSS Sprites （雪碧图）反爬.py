# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/25
📄File       : n05-CSS Sprites （雪碧图）反爬.py
ℹ️Description: 简短描述该文件的主要功能或目的

同伪类的相识，不过是直接去获取完整的类，不需要像伪类那样需要拼接，且网页中没有提供对应的值，
只能找到雪碧图，看看其内有哪些数据，然后一个一个在网页中试出来，在构建好数据

雪碧图： [0,1,2,3,4,5,6,7,8,9]
他们每个值都可以在网页中找到对应的类属性，获取类属性对应的值构建成字典。
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
    sprite_chart = {
        'sprite abcdef': '0',
        'sprite ghijkl': '1',
        'sprite mnopqr': '2',
        'sprite uvwxyz': '3',
        'sprite yzabcd': '4',
        'sprite efghij': '5',
        'sprite klmnop': '6',
        'sprite wxyzab': '8',
        'sprite cdefgh': '9'
    }
    data = []
    dom_tree = etree.HTML(html)
    divs = dom_tree.xpath('//div[@class="container"]/div/div')
    for div in divs:
        title = div.xpath('./h2/text()')[0]
        ranking = div.xpath('./p[1]/text()')[0].replace('排名：', '')
        value = div.xpath('./p[2]/span/@class')
        value = ''.join(map(lambda i: sprite_chart[i], value))
        ceo_name = div.xpath('./p[3]/text()')[0].replace('CEO：', '')
        profession = div.xpath('./p[4]/text()')[0].replace('行业：', '')

        dic = {'企业': title,
               '排名': ranking,
               '企业估值(亿元)': value,
               'CEO': ceo_name,
               '行业': profession}
        print(dic)
        data.append(dic)
    return data


def save_data(datas, file_name='n05胡润中国500强.csv'):
    """数据保存"""
    fieldnames = ['企业', '排名', '企业估值(亿元)', 'CEO', '行业']
    path = os.path.join(save_directory, file_name)

    with open(path, 'w', newline='', encoding='utf-8') as w_f:
        writer = csv.DictWriter(w_f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(datas)


def main():
    url = 'http://www.spiderbuf.cn/n05/'
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