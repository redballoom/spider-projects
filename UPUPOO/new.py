# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/29
📄File       : new.py
ℹ️Description: 简短描述该文件的主要功能或目的

这里我想使用进程池来创建6个进程，抓取6个页面，且每个进程中在使用线程池来下载图片
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter

# 配置常量
FOLDER = 'img'
TAG_ID = 12
TOTAL_PAGE = 6  # 总页数

# 创建目录（如果不存在）
folder_path = Path(FOLDER)
folder_path.mkdir(parents=True, exist_ok=True)

# 配置请求重试策略
retries = Retry(
    total=3,  # 总重试次数
    backoff_factor=1,  # 指数退避因子
    allowed_methods=frozenset(['GET', 'POST']),  # 允许重试的HTTP方法
)
adapter = HTTPAdapter(max_retries=retries)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)

# 设置请求头
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) upupoo-wallpaper-shop/0.0.1 Chrome/80.0.3987.165 Electron/8.2.5 Safari/537.36',
})


def get_page(method, url, **kwargs):
    """
    发送HTTP请求获取响应对象。

    Args:
        method (str): HTTP方法，如`GET`、`POST`等。
        url (str): 要请求的URL。
        **kwargs: request支持的所有参数。

    Returns:
        requests.Response: HTTP响应对象。如果出错，返回None。
    """
    try:
        response = session.request(method, url, timeout=10, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error making {method} request to {url}: {e}")
        return None


def get_index_page(page):
    """
    获取指定页码的索引页数据。

    Args:
        page (int): 页码。

    Returns:
        requests.Response: HTTP响应对象。
    """
    url = 'https://pcwallpaper.upupoo.com/wallpaper/lists'
    data = {
        "current": page,
        "size": 28,
        "total": 239311,
        "type": 0,
        "tagId": TAG_ID,
        "sort": 0,
        "resolution": 0,
        "hairtail": 0
    }
    return get_page('POST', url, json=data)


def parse(json_data):
    """
    解析JSON数据，生成图片ID和URL。

    Args:
        json_data (dict): JSON数据。

    Yields:
        tuple: 图片ID和图片URL。
    """
    records = json_data.get('data', {}).get('records', [])
    for info in records:
        paper_id = info['paper_id']
        img_url = info['img_url']
        new_img_url = img_url.replace('listCover.jpg', 'previewFix.jpg')
        yield paper_id, new_img_url


def download(data):
    """
    下载图片并保存到本地。

    Args:
        data (tuple): 图片ID和图片URL。
    """
    name, url = data
    response = get_page('GET', url)
    if response:
        file_path = folder_path / f'{name}.jpg'
        with file_path.open('wb') as f:
            f.write(response.content)
        print(f'Successful -> {url}')
    else:
        print(f'Failed to download -> {url}')


def start_thread_pool(func, iterable):
    """
    启动线程池并行执行任务。

    Args:
        func (callable): 要并行执行的函数。
        iterable (iterable): 任务的可迭代对象。
    """
    with ThreadPoolExecutor(max_workers=12) as executor:
        executor.map(func, iterable)


def main():
    """
    主函数，启动进程池获取数据，并启动线程池下载图片。
    """
    with ProcessPoolExecutor(max_workers=6) as process_executor:
        # 创建一个生成器，获取每一页的数据，并解析图片信息
        img_tasks = (
            img for html in process_executor.map(get_index_page, range(1, TOTAL_PAGE + 1))
            if html is not None
            for img in parse(html.json())
        )
        # 启动线程池下载图片
        start_thread_pool(download, img_tasks)


if __name__ == '__main__':
    main()
