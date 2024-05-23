# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/21
📄File       : new_demo.py
ℹ️Description: 简短描述该文件的主要功能或目的

目标地址: https://www.ruanyifeng.com/blog/weekly/
"""
import urllib3
from urllib3.util import Retry
from typing import Generator, List, Dict, Optional

from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter
from loguru import logger
from pyquery import PyQuery

ua = UserAgent().random  # 随机UA
# 禁止显示InsecureRequestWarning警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()


def get_request(url: str) -> Optional[str]:
    """
    通用get请求方法
    :param url: 目标网站的url链接
    :return: 目标网站的源代码信息
    """
    retries = Retry(total=3, backoff_factor=1)  # 重试3次，重试间隔1s
    session.mount('https://', HTTPAdapter(max_retries=retries))
    headers = {"User-Agent": ua}
    try:
        response = session.get(url, headers=headers, timeout=6, verify=False)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during request: {e}")
        return None


def parse_page(html: str) -> Generator[str, None, None]:
    """
    解析页面数据，获取详情页url
    :param html: 网页源代码数据
    :return: Generator[href] 包含详情页链接的生成器
    """
    doc = PyQuery(html)  # 初始化PyQuery
    li_list = doc('#alpha-inner ul.module-list li').items()
    for li in li_list:
        href = li('a').attr('href')  # 300条
        yield href


def get_detail_page(url: str) -> Optional[str]:
    """通过获取的详情页url，在内部调用get_request方法来获取详情页数据"""
    logger.info(f"Start parsing the {url}...")
    return get_request(url)


def detail_parse_page(detail_html: str) -> List[Dict[str, str]]:
    """解析详情页，拿到最终数据"""
    doc = PyQuery(detail_html)
    resources = []
    try:
        # 找到 <h2> 资源
        resource_section = doc('h2:contains("资源")')
        # 获取资源后的所有同级 <p> 标签直到遇到下一个同级 <h2>
        current_item = {}

        for sibling in resource_section.next_all():
            if sibling.tag == 'h2':
                break
            if sibling.tag == 'p':
                p = PyQuery(sibling)
                if p('a').length > 0 and 'title' not in current_item:
                    current_item = {
                        'title': p('a').text(),
                        'href': p('a').attr('href'),
                        'desc': ''
                    }
                elif p('img').length > 0:
                    current_item['img'] = p('img').attr('src')
                elif p.text():
                    current_item['desc'] = p.text()
                    if 'title' in current_item:
                        resources.append(current_item)
                        current_item = {}
        return resources
    except Exception as e:
        logger.error(f"An error occurred while parsing the HTML content: {e}")
        return []


def main():
    page_url = "https://www.ruanyifeng.com/blog/weekly/"
    page_html = get_request(page_url)
    if not page_html:
        logger.error("Failed to retrieve the main page.")
        return
    generate_url = parse_page(page_html)
    for detail_url in generate_url:  # 300
        detail_page = get_detail_page(detail_url)
        if detail_page:
            resource_data = detail_parse_page(detail_page)  # 一个detail_url的数据
            logger.info(resource_data)


if __name__ == '__main__':
    main()
