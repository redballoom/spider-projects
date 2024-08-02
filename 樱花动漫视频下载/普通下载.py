#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import re

import requests

"""此版本为单线程普通下载"""


def get_page(url, retry=3):
    """
    通用请求方法，用于发起get请求
    :param url: 请求视频的url
    :param retry: 请求重试最大数
    :return: response or None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    i = 1
    while i <= retry:
        try:
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(e)
            i += 1
            time.sleep(i * 2)
    else:
        print("达到最大重试次数，返回 None")
        return None


def get_m3u8_file(url, folder_name, file_name='index.m3u8'):
    doc_html = get_page(url)
    m3u8_url = re.search(r'onClick="changeplay\(\'(?P<url>.*?)\$', doc_html, re.S).group('url')
    data = get_page(m3u8_url)
    path = os.path.join(folder_name, file_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
    return m3u8_url


def download_ts(url, folder_name, file_name='index.m3u8'):
    """
    下载ts文件并保存到指定目录
    :param url:
    :param folder_name:
    :param file_name:
    :return:
    """
    """
    https://c1.rrcdnbf3.com/video/shixiongashixiong/%E7%AC%AC48%E9%9B%86/0000000.ts
    https://c1.rrcdnbf3.com/video/shixiongashixiong/%E7%AC%AC48%E9%9B%86/0000001.ts
    """
    path = os.path.join(folder_name, file_name)
    with open(path, 'r', encoding='utf-8') as f:
        data_lines = f.readlines()
    for line in data_lines:
        if line.startswith('#') and not line.startswith('0'):
            continue
        else:
            host = url.rsplit('/', 1)[0]
            ts_name = line.strip('\n')
            ts_url = host + '/' + ts_name
            ts_content = requests.get(ts_url).content
            ts_path = os.path.join(folder_name, ts_name)
            with open(ts_path, 'wb') as f:
                f.write(ts_content)
                f.flush()
                print(f'{ts_url} -- succeed!')


def merge_ts(folder, output):
    """
    合并ts文件为MP4文件，并删除原始的ts文件。

    :param folder: ts文件的文件夹路径。
    :param output: 合并后输出的MP4文件名。
    """
    index_m3u8_path = os.path.join(folder, 'index.m3u8')
    output = os.path.join(output)
    cmd = rf'ffmpeg -i {index_m3u8_path} -c copy {output}.mp4'
    os.system(cmd)
    print(f'{output}.mp4 -- merge complete!')

    # 删除TS文件
    for file in os.listdir(folder):
        if file.endswith(".ts"):
            os.remove(os.path.join(folder, file))


if __name__ == '__main__':
    ts_folder = 'TS'
    if not os.path.exists(ts_folder):
        os.mkdir(ts_folder)
    page_url = 'http://www.iyinghua.io/v/5836-48.html'

    m3u8_url_link = get_m3u8_file(page_url, ts_folder)
    output_name = m3u8_url_link.rsplit('/', 2)[1]
    download_ts(m3u8_url_link, ts_folder)
    merge_ts(ts_folder, output_name)
