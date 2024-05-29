# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : s04-分页参数分析及翻页爬取.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/s04/

分页规律：
    http://www.spiderbuf.cn/s04/?pageno=1
    http://www.spiderbuf.cn/s04/?pageno=2

分页参数：pageno
"""
# 导入需要的库
from urllib.parse import urljoin
import os.path

import requests
from lxml import etree


def get_page(url, headers=None, **kwargs):
    """
    通用get请求获取页面源码
    :param url: 请求链接
    :param headers: 请求头
    :return: 响应对象response
    """
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=default_headers, timeout=10, **kwargs)
        response.raise_for_status()  # 如果不是2xx状态码请求，则抛出HTTPError错误
        return response.text
    except requests.exceptions.RequestException as e:  # 通用requests异常捕获
        print(f"Error making request to {url}: {e}")
        return None


def get_index_page(total_page):
    """获取多页url链接，并返回url的生成器"""
    for page in range(1, total_page + 1):
        # 构建特定页码的 URL
        url = urljoin(base_url, f'/s04/?pageno={page}')
        yield url


def lxml_parse(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html:
    :return: page_data_list: 一页的数据列表
    """
    dom_tree = etree.HTML(html)
    trs = dom_tree.xpath('/html/body/div/div[1]/table/tbody/tr')  # 如果不熟悉xpath语法，可以直接在控制台元素位置copy
    # 通用方法：先定位到一个个“盒子”，再从“盒子”中遍历取数据。
    page_data_list = []  # 存放一页的数据
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
        page_data_list.append(file_data)
    return page_data_list


def save_data(data_list, file_name='s04-设备信息.txt'):
    """数据保存"""
    folder_name = 'datas'
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    path = os.path.join(folder_name, file_name)  # 完整文件路径
    with open(path, mode='a', encoding='utf-8') as f:
        f.writelines(data_list)


if __name__ == '__main__':
    # 此内相当于全局环境
    PAGE = 5  # 要获取的页码数量
    base_url = 'http://www.spiderbuf.cn/'
    gen_url = get_index_page(PAGE)  # 获取多页的url生成器
    # 我们在处理大量数据存储时应避免一个一个添加，这样效率低，开销大，在处理完数据直接一次性存储会更好。但是
    # 如果数据量很大，一次性存储可能会导致内存不足的问题。在这种情况下，可以采用分批次处理的方法。
    # 我一般都选择分批次处理（按页处理），这样在中断程序时也能保证一部分数据的存储。
    # 总之，在处理大量数据时，需要根据具体情况来选择合适的方法。一次性存储和分批次处理都可能是有用的选择。
    for page_url in gen_url:
        print(f'当前处理网页：{page_url}')
        # 调用你的爬取函数来处理这个特定页码的数据
        html_data = get_page(page_url)
        # 调用解析函数
        one_page_data = lxml_parse(html_data)
        save_data(one_page_data)
