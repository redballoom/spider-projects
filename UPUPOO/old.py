# -*- coding: utf-8 -*-
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2024年01月01
@ 📄File       : old.py
@ ℹ️Description:

采集 UPUPOO 的壁纸

使用工具:
  Progress Telerik Fiddler Classic
  pycharm

"""
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

FOLDER = 'wallpaper'
TAG_ID = 12
TOTAL_PAGE = 6  # 总页数

folder_path = Path(FOLDER)
# 创建目录（如果不存在）parents: 允许父目录，exist_ok: 如果存在也不发生报错
Path.mkdir(folder_path, exist_ok=True)


def get_page(method, url, headers=None, **kwargs):
    """
    发送HTTP请求获取网页内容。

    Args:
        method (str): HTTP方法，如`GET`、`POST`等。
        url (str): 要请求的URL。
        headers (dict, optional): 用于请求的HTTP头。默认为None。
        **kwargs: request支持的所有参数。

    Returns:
        requests.Response: HTTP响应对象。如果出错，返回None。
    """
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) upupoo-wallpaper-shop/0.0.1 Chrome/80.0.3987.165 Electron/8.2.5 Safari/537.36',
    }

    try:
        resp = requests.request(method, url, headers=default_headers, timeout=10, **kwargs)
        resp.raise_for_status()
        return resp
    except requests.exceptions.RequestException as e:
        print(f"Error making {method} request to {url}: {e}")
        return None


def get_index_page(page):
    url = 'https://pcwallpaper.upupoo.com/wallpaper/lists'
    data = {"current": page, "size": 28, "total": 239311, "type": 0,
            "tagId": TAG_ID, "sort": 0, "resolution": 0, "hairtail": 0}
    return get_page('POST', url, json=data)


def parse(json_data):
    cards = json_data['data']['records']  # 字典数据列表:
    for info in cards:
        paper_id = info['paper_id']
        img_url = info['img_url']

        # https://pcsource.upupoo.com/theme/2001206385/listCover.jpg
        # 这个链接是小图，大图需要把listCover换为previewFix
        new_filename = 'previewFix.jpg'
        parts = img_url.split('/')
        # 替换文件名
        parts[-1] = new_filename
        new_img_url = '/'.join(parts)
        yield paper_id, new_img_url


def download(data):
    # data 是一个生成器 里面是元组 (id, url)
    name, url = data  # 使用解包是很好的选择，如果使用循环会导致多进程不能成功工作
    response = get_page('GET', url)
    # 这里使用一个判断是很好的选择，以免错误的返回None,导致使用response.content报错
    if response:
        img_content = response.content
        file_path = folder_path / f'{name}.jpg'  # 确保文件名的正确性
        with open(file_path, mode='wb') as f:
            f.write(img_content)
            print(f'Successful -> {url}')
    else:
        print('Response has no content.')


def start_thread_pool(func, iterable):
    # 建议不要将max_workers设置太大，应避免给对方服务器造成压力，尤其是请求页数多的时候
    with ThreadPoolExecutor(max_workers=12)as executor:
        executor.map(func, iterable)


if __name__ == '__main__':
    for i in range(1, TOTAL_PAGE + 1):
        html = get_index_page(i)
        parse(html.json())
        g_data = parse(html.json())
        # 启动进程池
        start_thread_pool(download, g_data)
