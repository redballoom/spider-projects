# 案例的成功取决于是否有高可用的代理ip，因为获取的ip太垃圾了，运行多几次就不行了。
# 反正遇到这样限制请求次数的网站，还想要提高请求效率的话，只要有高可用的代理ip，便可以轻松解决。
# 如果找不到免费可用的代理ip的话，可以去github上找找

import csv
import random
import time
import os.path
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

import requests
from lxml import etree


def get_page(url, headers=None, retries=3):
    ip_data = ['198.44.255.3:80', '47.242.47.64:8888']  # 假装是ip池
    # 使用random.choice函数随机选择一个元素
    random_ip_port = random.choice(ip_data)
    proxies = {
        'http': f'http://{random_ip_port}',
        'https': f'https://{random_ip_port}',
    }
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=default_headers, proxies=proxies, timeout=10)
            response.raise_for_status()  # 如果不是200状态码请求，则抛出HTTPError错误
            return response.text
        except requests.exceptions.RequestException as e:  # 通用异常捕获
            print(f"Error making request to {url}: {e}. Attempt {attempt + 1} of {retries}.")
    return None


def get_index_page(page_url):
    """获取多页数据"""
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


def save_data(datas, file_name='n03-多进程加速-密码列表.csv'):
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

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(get_index_page, [urljoin(base_url, f'/n03/{page}') for page in range(1, total_page + 1)])


if __name__ == '__main__':
    main()
