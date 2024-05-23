# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/16
📄File       : 详情页.py
ℹ️Description: 从获取的data.csv文件中读取详情页的url,获取陶贴收藏帖子的数据情况

"""
import csv
import pandas as pd
from pathlib import Path
from time import sleep
from random import choice
from urllib.parse import urljoin

import requests
from pyquery import PyQuery

base_url = 'https://www.52pojie.cn/'
file_name = 'detail_page_data2.csv'

fieldnames = ['title', 'url', 'author', 'created_time', 'recover', 'view']
with open(file_name, 'w', newline='', encoding='utf-8') as w_file:
    writer_header = csv.DictWriter(w_file, fieldnames=fieldnames)
    writer_header.writeheader()


def read_csv():
    """从文件中读取详情页url"""
    path = Path('./data.csv')
    if not path.exists():
        raise FileNotFoundError('data.csv not found')
    else:
        data = pd.read_csv(path, encoding='utf-8')
        urls = data['album_url'].tolist()
        return urls


def get_page_html(page_url: str):
    """通用GIT请求方法"""
    print(f"Current url is {page_url}")
    try:
        response = requests.get(page_url)
        cho = [0.5, 0.8, 1, 1.2, 1.5, 1.8, 2, 2.5]
        sleep(choice(cho))  # 控制请求频率，避免触发429请求过多的错误
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to get page HTML: {e}")
        return None


def fetch_next_page(page_url):
    """发送请求获取详情页的下一页的HTML"""
    next_page_html = get_page_html(page_url)
    if next_page_html:
        return next_page_html
    else:
        return None


def get_next_page_url(html):
    """从页面中获取下一页的链接"""
    doc = PyQuery(html)
    next_page = doc('div.pg a.nxt') if doc('div.pg a.nxt') else ''
    if next_page:
        next_href = next_page.attr('href')
        next_url = urljoin(base_url, next_href)
        return next_url
    else:
        return None


def parse_detail_page(html):
    """解析页面数据"""
    doc = PyQuery(html)
    # 解析数据
    trs = doc('.tl > .bm_c tr').items()  # 一页50个
    page_data = []  # 不管有多少页数据都放进来
    for tr in trs:
        title = tr('th > a').text().strip()
        href = tr('th > a').attr('href').strip()
        url = urljoin(base_url, href)
        author = tr('td:nth-child(3) a').text().strip()
        created_time = tr('td.by em.xi1').text().strip()
        recover = tr('td.num a').text().strip()
        view = tr('td.num em').text().strip()

        row_data = {
            'title': title,
            'url': url,
            'author': author,
            'created_time': created_time,
            'recover': recover,
            'view': view,
        }
        page_data.append(row_data)

    next_page_url = get_next_page_url(html)
    if next_page_url:
        next_page_html = fetch_next_page(next_page_url)
        if next_page_html:
            return parse_detail_page(next_page_html)
        else:
            print("Failed to fetch next page.")
            return save(page_data)
    else:
        print("No more pages available.")
        return save(page_data)


def save(data):
    with open(file_name, 'a', newline='', encoding='utf-8') as a_file:
        writer_row = csv.DictWriter(a_file, fieldnames=fieldnames)
        for row in data:
            writer_row.writerow(row)


def main():
    try:
        album_urls = read_csv()
        for url in album_urls:
            detail_page_html = get_page_html(url)
            parse_detail_page(detail_page_html)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
