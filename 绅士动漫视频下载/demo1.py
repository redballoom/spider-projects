#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import time
import json
from urllib.parse import urljoin

from lxml import etree
import requests

"""经过GPT优化后的版本"""


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
            print(f"请求失败，尝试次数：{i}, 错误信息：{e}")
            i += 1
            time.sleep(i * 2)
    print("达到最大重试次数，返回 None")
    return None


def get_index_page(url):
    """
    通过下载索引页的数据，提取出当前动漫所包含的所有集的url
    :param url: 索引页url
    :return: 动漫集数链接的生成器
    """
    html_data = get_page(url)
    if html_data:
        tree = etree.HTML(html_data)
        a_list = tree.xpath('//div[@class="module-play-list"]/div/a/@href')
        for a in a_list:
            play_url = urljoin('https://1anime.me/', a)
            yield play_url
    else:
        print("未能获取到索引页数据")


def download_m3u8(url, folder_path):
    """
    根据生成器返回的集数链接，下载对应m3u8文件
    :param url: 集数链接
    :param folder_path: 保存m3u8文件的文件夹路径
    :return: 下载的m3u8文件路径
    """
    doc_html = get_page(url)
    try:
        player_json = re.search(r'var player_aaaa=(.*?)</script>', doc_html, re.S).group(1)
        player_dict = json.loads(player_json)
        m3u8_url = player_dict['url']
        if m3u8_url.endswith('.m3u8'):
            m3u8_file_path = os.path.join(folder_path, m3u8_url.split('/')[-1])
            m3u8_data = get_page(m3u8_url)
            with open(m3u8_file_path, mode='w', encoding='utf-8') as f:
                f.write(m3u8_data)
            return m3u8_url, m3u8_file_path
    except (AttributeError, json.JSONDecodeError) as e:
        print(f"解析player_json失败: {e}")
        return None


def download_ts(path, folder_path):
    """
    下载m3u8文件中的所有ts文件
    :param path: m3u8文件路径
    :param folder_path: 保存ts文件的文件夹路径
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('#'):
            continue
        else:
            ts_url = 'https://cdn.s3.6782563.xyz/vod/hdb/70302/data/01_cykfihd9pi/' + line.strip()
            print(f'{ts_url} -- downloading...')
            try:
                ts_content = requests.get(ts_url).content
                ts_path = os.path.join(folder_path, line.strip())
                with open(ts_path, mode='wb') as f:
                    f.write(ts_content)
                    f.flush()
            except requests.exceptions.RequestException as e:
                print(f"下载 {ts_url} 失败: {e}")


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
    index_url = 'https://1anime.me/voddetail/8183.html'
    ts_folder = 'ts'
    if not os.path.exists(ts_folder):
        os.mkdir(ts_folder)

    playlist = get_index_page(index_url)  # 动漫集数链接的生成器

    try:
        url = next(playlist)  # 取出第一集的链接
        print(f'开始下载 -- {url}')
        m3u8_url, m3u8_path = download_m3u8(url, ts_folder)
        if os.path.exists(m3u8_path):
            download_ts(m3u8_path, ts_folder)
        else:
            print("未能下载m3u8文件")
    except StopIteration:
        print("未能获取到任何集数链接")
