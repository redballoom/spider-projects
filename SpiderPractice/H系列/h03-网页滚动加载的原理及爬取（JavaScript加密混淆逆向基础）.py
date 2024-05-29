# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : h03-网页滚动加载的原理及爬取（JavaScript加密混淆逆向基础）.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/h03/
这个网页是有问题的，在下拉后并没有像预料的那样更新新内容。

-- 第一页的最后一个是泰坦尼克号。
5f685274073b -- 2
279fcd874c72 -- 3
8a3d4d640516 -- 4

http://www.spiderbuf.cn/h03/5f685274073b 接口链接形式，确定接口是第几页可以复制 /5f685274073b 到XHR断点调试知晓

其实就是ajax动态加载数据的爬取。其实也不难，直接打开控制台查看XHR的接口信息，定位到数据接口，分析它的有没有携带控制页数的参数（载荷）
然后判断，哪些是固定值，哪些是动态值，逆向出动态值后构造出请求时要携带的请求参数即可。这是通用的逻辑，但具体还得看实际情况。

“代码经过GPT优化后，具备了良好的可读性、健壮性和扩展性，降低了学习难度，提高了编码效率和编程思维。”
"""
import os
import time
from typing import Generator, Optional, List, Dict
from urllib.parse import urljoin

import requests
from lxml import etree

FOLDER_NAME = 'datas'
os.makedirs(FOLDER_NAME, exist_ok=True)


def get_page(url: str, headers: Optional[dict] = None, retries: int = 3) -> Optional[str]:
    """
    通用请求方法，支持重试
    :param url: 请求的URL
    :param headers: 请求头
    :param retries: 重试次数
    :return: 响应文本或None
    """
    default_headers = headers or {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'),
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(2 ** attempt)  # 指数退避策略
    return None


def get_api_url(url: str, html: Optional[str] = None) -> Generator[str, None, None]:
    """
    生成下一页的URL
    :param url: 基础URL
    :param html: 网页源码
    :return: 下一页的URL生成器
    """
    if html is None:
        html = get_page(url)
        if not html:
            return

    dom_tree = etree.HTML(html)
    while html:
        next_paths = dom_tree.xpath('//div[@id="sLaOuol2SM0iFj4d"]/text()')
        if next_paths:
            next_path = next_paths[0]
            next_page_url = urljoin(url, next_path)
            yield next_page_url
            html = get_page(next_page_url)
            if html:
                dom_tree = etree.HTML(html)
            else:
                break
        else:
            print('No next page found.')
            break


def parse_page(html: str) -> List[Dict[str, str]]:
    """
    解析网页内容
    :param html: 网页源码
    :return: 解析后的数据列表
    """
    dom = etree.HTML(html)
    div_list = dom.xpath('//div[contains(@class, "row") and contains(@style, "margin-top: 10px;")]/div')[::2]  # 隔行取值，筛选掉简介
    parsed_data = []
    for div in div_list:
        title = div.xpath('./h2/text()')[0]
        scores = div.xpath('./div[2]/span[contains(text(),"豆瓣电影评分:")]/following::text()[1]')[0]
        parsed_data.append({'title': title, 'scores': scores})
    return parsed_data


def save_data(data: List[Dict[str, str]], file_name: str = 'h03电影信息.csv') -> None:
    """
    数据保存
    :param data: 需要保存的数据
    :param file_name: 文件名
    """
    path = os.path.join(FOLDER_NAME, file_name)
    with open(path, 'a', encoding='utf-8') as f:
        for item in data:
            f.write(f"{item['title']},{item['scores']}\n")
        print('保存完毕')


def main() -> None:
    base_url = 'http://www.spiderbuf.cn/h03/'
    # 接口链接的形式是从第二页开始的，第一页我们需单独处理
    index_page_html = get_page(base_url)
    if index_page_html:
        index_page_data = parse_page(index_page_html)
        save_data(index_page_data)

        gen_next_url = get_api_url(base_url, index_page_html)
        for next_url in gen_next_url:
            html_data = get_page(next_url)
            if html_data:
                parsed_data = parse_page(html_data)
                save_data(parsed_data)


if __name__ == '__main__':
    main()

