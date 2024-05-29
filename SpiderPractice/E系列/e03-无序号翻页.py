# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : e03-无序号翻页.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/e03/

http://www.spiderbuf.cn/e03/2fe6286a4e5f  1
http://www.spiderbuf.cn/e03/5f685274073b  2
控制翻页的不在是普通数字，而是在前端代码中页码位置，只要获取下来拼接到链接后即可
"""

# 导入需要的库
import os.path
from urllib.parse import urljoin

import requests
from lxml import etree

base_url = 'http://www.spiderbuf.cn/e03/'
FOLDER_NAME = 'datas'
if not os.path.exists(FOLDER_NAME):
    os.mkdir(FOLDER_NAME)


def get_page(url, headers=None, retries=3):  # retries: 自定义重试3次
    """通用请求方法"""
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


def get_index_page_url(url):
    """
    通过获取页码的路径来拼接出完整的请求链接，返回page_url的生成器
    :param url: base_url的链接
    :return: page_url
    """
    html_data = get_page(url)
    # 添加判断，在重试三次后html_data的值为None 则直接退出程序
    if not html_data:
        return
    dom_tree = etree.HTML(html_data)
    page_path_list = dom_tree.xpath('//ul[@class="pagination"]/li/a/@href')
    for page_path in page_path_list:
        page_url = urljoin(url, page_path)  # 通过urljoin来拼接路径
        print(f'采集当前页数据：{page_url}')
        yield page_url


def lxml_parse(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html: 一页的网页源代码数据
    :return: 解析后的一页数据列表
    """
    dom_tree = etree.HTML(html)
    trs = dom_tree.xpath('//table[@class="table"]/tbody/tr')
    page_data = []
    for tr in trs:
        ranking = tr.xpath('./td[1]/text()')[0]
        value = tr.xpath('./td[2]/text()')[0]
        enterprise_information = tr.xpath('./td[3]/text()')[0]
        ceo_name = tr.xpath('./td[4]/text()')[0]
        profession = tr.xpath('./td[5]/text()')[0]
        row_data = ','.join([ranking, value, enterprise_information, ceo_name, profession, '\n'])
        page_data.append(row_data)
    return page_data


def save_data(file_data, file_name='e03胡润中国500强.txt'):
    """数据保存"""
    path = os.path.join(FOLDER_NAME, file_name)  # 完整文件路径
    with open(path, mode='a', encoding='utf-8') as f:
        f.writelines(file_data)


def main():
    gen_page_url = get_index_page_url(base_url)
    for page_url in gen_page_url:
        page_html = get_page(page_url)
        if page_html:
            page_data = lxml_parse(page_html)
            save_data(page_data)
        else:
            print(f"Failed to retrieve or parse page: {page_url}")


if __name__ == '__main__':
    main()
