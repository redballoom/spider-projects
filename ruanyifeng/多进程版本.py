# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/23
📄File       : 多进程版本.py
ℹ️Description: 添加进程池来提高请求效率

"""
import json
import urllib3
from urllib3.util import Retry
from concurrent.futures import ThreadPoolExecutor
from typing import Generator, List, Dict, Optional

from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter
from loguru import logger
from pyquery import PyQuery

# 禁止显示InsecureRequestWarning警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ua = UserAgent().random  # 随机UA

session = requests.Session()
session.headers.update({"User-Agent": ua})


def get_request(url: str) -> Optional[str]:
    """
    通用GET请求方法。
    :param url: 目标网站的URL。
    :return: 目标网站的源代码。
    """
    retries = Retry(total=3, backoff_factor=1)  # 重试3次，重试间隔1s
    session.mount('https://', HTTPAdapter(max_retries=retries))
    try:
        response = session.get(url, verify=False)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during request: {e}")
        return None


def parse_page(html: str) -> Generator[str]:
    """
    解析页面数据以获取详情页面url。
    :param html: 网页源代码。
    :return: 包含详细页面链接的生成器。
    """
    doc = PyQuery(html)
    li_list = doc('#alpha-inner ul.module-list li').items()
    for li in li_list:
        href = li('a').attr('href')
        if href:
            yield href


def get_detail_page(url: str) -> Optional[str]:
    """通过调用get_request方法获取详情页数据。"""
    logger.info(f"Start parsing the {url}...")
    return get_request(url)


def detail_parse_page(detail_html: str) -> List[Dict[str, str]]:
    """解析详情页，提取最终数据。"""
    doc = PyQuery(detail_html)
    resources = []
    try:
        resource_section = doc('h2:contains("资源")')
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


def save_json(data: List[Dict[str, str]], filename: str = 'resource_data.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"An error occurred while writing to the file: {e}")


def main():
    page_url = "https://www.ruanyifeng.com/blog/weekly/"
    page_html = get_request(page_url)
    if not page_html:
        logger.error("Failed to retrieve the main page.")
        return

    generate_url = parse_page(page_html)
    all_resource_data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_detail_page, url) for url in generate_url]

        for future in futures:
            detail_page = future.result()  # 返回get_detail_page的调用结果
            if detail_page:
                resource_data = detail_parse_page(detail_page)
                logger.info(resource_data)
                all_resource_data.extend(resource_data)

    save_json(all_resource_data)


if __name__ == '__main__':
    main()
