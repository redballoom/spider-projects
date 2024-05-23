# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月08
@ 📄File       : jijian.py
@ ℹ️Description: 爬取极简壁纸的图片

图片地址：
https://api.zzzmh.cn/bz/v3/getUrl/c071cdc46f0c4867a1d52d0cb51fc6d6 2 9
https://api.zzzmh.cn/bz/v3/getUrl/a47a423f9d1c42f8895c53c72f27ff87 2 9
https://api.zzzmh.cn/bz/v3/getUrl/2ed7cfb8882411ebb6edd017c2d2eca2 1 9
https://api.zzzmh.cn/bz/v3/getUrl/8373377e69c3499d904877fab8c6f329 2 9
https://api.zzzmh.cn/bz/v3/getUrl/aaee8a7dfce749259b5cf6924f1c235b 2 9
对比我们返回的数据可发现图片下载链接是由 https://api.zzzmh.cn/bz/v3/getUrl 拼接 i 的值 + t的值 + 固定的9构成


"""
import time

import requests
import json
import execjs
from pathlib import Path

base_url = 'https://bz.zzzmh.cn/'
folder = 'Wallpaper'
folder_path = Path(folder)
# 创建目录（如果不存在）parents: 允许父目录，exist_ok: 如果存在也不发生报错
folder_path.mkdir(parents=True, exist_ok=True)


def get_page(method, url, headers=None, **kwargs):
    """
    通用请求获取网页内容。

    Args:
        method (str): HTTP方法，如''GET''、''POST''等。
        url (str): 要请求的URL。
        headers (dict, optional): 用于请求的HTTP头。默认为None。
    Returns:
        requests.Response: HTTP响应对象。如果出错，返回None。
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    headers = headers or default_headers

    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error making {method} request to {url}: {e}")
        return None


def get_index(page):
    """
    通过page页码获取响应数据
    
    Args:
        page (int): 页码，从1开始计数
    Returns:
        response响应对象: 返回请求到的数据索引的响应对象   
    """
    api_url = 'https://api.zzzmh.cn/bz/v3/getData'
    data = {
        "size": 24,
        "current": page,
        "sort": 0,
        "category": 0,
        "resolution": 0,
        "color": 0,
        "categoryId": 0,
        "ratio": 0
    }
    return get_page('POST', api_url, json=data)


def parse(data):
    """
    解析加密后的json数据，并返回图片ID和下载链接的生成器。
    
    Args:
        data (str): 加密后的json数据字符串。
    Returns:
        Generator[Tuple[str, str], None, None]: 包含图片ID和下载链接的元组生成器。
    
    """
    dict_data = json.loads(data)  # 解析json数据,转为python字典
    result = dict_data['result']  # 加密的数据
    with open('cc.js', mode='r', encoding='utf-8') as f:
        js_code = f.read()
    # 编译js代码
    ctx = execjs.compile(js_code)
    json_data = ctx.call('run', result)
    # 将解码的json数据转为python字典
    info_data = json.loads(json_data)
    for i in info_data['list']:
        pic_id = i['i']
        pic_t = i['t']

        # 构造图片下载链接
        pic_url = f'https://api.zzzmh.cn/bz/v3/getUrl/{pic_id}{pic_t}9'
        yield pic_id, pic_url  # 返回文件名和链接


def download(name, url):
    headers = {
        # "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        # "Content-Type": "application/json;charset=UTF-8",
        # "Content-Length": "41",
        # "Origin": "https://bz.zzzmh.cn",
        "Referer": "https://bz.zzzmh.cn/",  # 403 防盗链处理
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    response = get_page('GET', url, headers=headers)
    if response:
        img_content = response.content
        save(img_content, name)
    else:
        print('检查请求是否返回了None!')


def save(data, file_name):
    file_path = Path(folder_path / f'{file_name}.jpg')
    with open(file_path, mode='wb') as f:
        f.write(data)
        print(f'{file_name}.jpg -- is OK.')


def main():
    for page in range(1, 2):
        response = get_index(page)
        pic_info_generator = parse(response.text)
        for name, url in pic_info_generator:
            download(name, url)


if __name__ == '__main__':
    s = time.time()
    main()
    print(f'耗时 {time.time() - s}')  # 耗时 186.8359887599945
