# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : n03-限制访问频率不低于1秒.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/n03/

对于限制了请求访问页面时间的网站，只需要在请求后添加time.sleep(N)即可，可这样就变得很慢，大大影响我们的心情，
这时就可以使用多线程或多进程来并行请求网页数据，前提是你得准备好可用的ip池
"""
import csv
import time
import os.path
from urllib.parse import urljoin

import requests
from lxml import etree


def get_page(url, headers=None, retries=3):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()  # 如果不是200状态码请求，则抛出HTTPError错误
            return response.text
        except requests.exceptions.RequestException as e:  # 通用异常捕获
            print(f"Error making request to {url}: {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(1)  # 重试前等待一段时间
    return None


def get_index_page(url, pages):
    """获取多页数据"""
    for page in range(1, pages + 1):
        # 构建特定页码的 URL,不建议字符串拼接的方式来构造url链接，可以使用urllib.parse的urljoin
        page_url = urljoin(url, f'/n03/{page}')
        # 调用你的爬取函数来处理这个特定页码的数据
        html_data = get_page(page_url)
        time.sleep(1)

        if html_data:
            print(f"Be dealing with：{page_url} ...")
            lxml_parse(html_data)
        else:
            print(f"Failed to retrieve data from {page_url}")


def lxml_parse(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html: 网页的源代码数据
    :return: None
    """
    dom_tree = etree.HTML(html)
    trs = dom_tree.xpath('//table[@class="table"]/tbody/tr')
    page_data = []
    for tr in trs:
        ranking = tr.xpath('./td[1]/text()')[0] if tr.xpath('./td[1]/text()') else ''
        pw = tr.xpath('./td[2]/text()')[0] if tr.xpath('./td[2]/text()') else ''
        cracking_time = tr.xpath('./td[3]/text()')[0].replace('< ', '') if tr.xpath('./td[3]/text()') else ''
        use_num = tr.xpath('./td[4]/text()')[0] if tr.xpath('./td[4]/text()') else ''

        dit = {
            'ranking': ranking,
            'password': pw,
            'cracking_time': cracking_time,
            'use_num': use_num,
        }
        page_data.append(dit)
    save_data(page_data)


def save_data(datas, file_name='n03-全球最常用密码列表.csv'):
    """数据保存"""
    save_directory = 'datas'
    os.makedirs(save_directory, exist_ok=True)  # exist_ok=True 如果目录已经存在，则不引发错误, False则反之

    fieldnames = ['ranking', 'password', 'cracking_time', 'use_num']
    path = os.path.join(save_directory, file_name)  # 完整文件路径
    file_exists = os.path.exists(path)
    with open(path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(datas)


def main():
    total_page = 5  # 要获取的页码数量
    base_url = f'http://www.spiderbuf.cn/'
    get_index_page(base_url, total_page)


if __name__ == '__main__':
    main()
