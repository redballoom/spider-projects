# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : e01-用户名密码登录爬取后台数据.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/e01/

一般我们在处理需要登录的页面时，都要先确保开发者工具中的保留日志已勾选，这是因为刷新页面或进行其他操作时，浏览器可能会清空之前的请求记录，导致无法捕获和查看所需的请求信息。

流程：
    - 打开开发者工具并勾选“保留日志”。
    - 点击登录按钮。
    - 查看和分析网络请求：
        -在“Network”面板中找到登录请求（通常是POST请求）。
        -查看请求的URL、请求头、请求体和响应数据。
        -复制需要的请求信息，用于模拟登录请求。

找到登录的页面: http://www.spiderbuf.cn/e01/login  POST 307
requests会自动处理重定向，所以通过post请求登录页面链接即可
"""
# 导入需要的库
import os.path

import requests
from lxml import etree


def get_page(url, headers=None, data=None, **kwargs):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    try:
        response = requests.post(url, headers=default_headers, data=data, timeout=10, **kwargs)
        response.raise_for_status()  # 如果不是2xx状态码请求，则抛出HTTPError错误
        return response.text  # 返回响应对象
    except requests.exceptions.RequestException as e:  # 通用异常捕获
        print(f"Error making request to {url}: {e}")
        return None


def parse(html):
    """
    解析数据
    :param html: 网页的源代码
    :return: page_data_list: 一页的数据信息
    """
    dom_tree = etree.HTML(html)
    # tr元素，一共50条
    trs = dom_tree.xpath('//table[@class="table"]/tbody/tr')
    page_data_list = []
    for tr in trs:
        ranking = tr.xpath('./td[1]/text()')[0]
        value = tr.xpath('./td[2]/text()')[0]
        enterprise_information = tr.xpath('./td[3]/text()')[0]
        ceo_name = tr.xpath('./td[4]/text()')[0]
        profession = tr.xpath('./td[5]/text()')[0]
        row_data = ','.join([ranking, value, enterprise_information, ceo_name, profession, '\n'])
        page_data_list.append(row_data)
    return page_data_list


def save_data(data_list, file_name='e01胡润中国500强.txt'):
    """数据保存"""
    folder_name = 'datas'
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    path = os.path.join(folder_name, file_name)  # 完整文件路径
    with open(path, mode='w', encoding='utf-8') as f:
        f.writelines(data_list)


if __name__ == '__main__':
    login_data = {'username': 'admin', 'password': '123456'}
    login_url = 'http://www.spiderbuf.cn/e01/login'
    html_data = get_page(login_url, data=login_data)
    page_data = parse(html_data)
    save_data(page_data)
