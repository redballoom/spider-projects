#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re

import aiohttp
import asyncio
import aiofiles


async def get_page(url, retry=3):
    """
    通用请求方法，用于发起GET请求并返回页面内容。

    :param url: 请求视频的URL。
    :param retry: 请求重试的最大次数，默认值为3次。
    :return: 返回请求页面的文本内容，如果失败则返回None。
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    i = 1
    while i <= retry:
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
        except aiohttp.ClientError as e:
            print(f"请求失败，尝试次数：{i}, 错误信息：{e}")
            await asyncio.sleep(i * 2)
            i += 1
    print("达到最大重试次数，返回 None")
    return None


async def get_m3u8_file(url, folder_name, file_name='index.m3u8'):
    """
    获取并保存M3U8文件。

    :param url: 包含M3U8文件URL的页面URL。
    :param folder_name: 保存M3U8文件的文件夹名称。
    :param file_name: 保存的M3U8文件名，默认值为 'index.m3u8'。
    :return: 返回M3U8文件的URL。
    """
    doc_html = await get_page(url)
    m3u8_url = re.search(r'onClick="changeplay\(\'(?P<url>.*?)\$', doc_html, re.S).group('url')
    data = await get_page(m3u8_url)
    path = os.path.join(folder_name, file_name)
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(data)
    return m3u8_url


async def download_ts_line(session, ts_url, ts_path):
    """
    下载单个ts文件并保存到指定路径。

    :param session: aiohttp会话对象。
    :param ts_url: ts文件的URL。
    :param ts_path: 保存ts文件的路径。
    """
    async with session.get(ts_url) as response:
        ts_content = await response.read()
    async with aiofiles.open(ts_path, 'wb') as f:
        await f.write(ts_content)
        await f.flush()
    print(f'{ts_url} -- succeed!')


async def download_ts(url, folder_name, file_name='index.m3u8'):
    """
    下载M3U8文件中所有的ts文件并保存到指定目录。

    :param url: M3U8文件的URL。
    :param folder_name: 保存ts文件的文件夹名称。
    :param file_name: M3U8文件名，默认值为 'index.m3u8'。
    """
    path = os.path.join(folder_name, file_name)
    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        data_lines = await f.readlines()

    tasks = []
    async with aiohttp.ClientSession() as session:
        for line in data_lines:
            if line.startswith('#') or line.startswith('/'):
                continue
            host = url.rsplit('/', 1)[0]
            ts_name = line.strip()
            ts_url = f'{host}/{ts_name}'
            ts_path = os.path.join(folder_name, ts_name)
            tasks.append(download_ts_line(session, ts_url, ts_path))
        await asyncio.gather(*tasks)


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


async def main():
    """
    主函数，执行下载和合并过程。
    """
    page_url = 'http://www.iyinghua.io/v/5836-1.html'
    folder_name = 'TS'
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    m3u8_url_link = await get_m3u8_file(page_url, folder_name)
    output_name = m3u8_url_link.rsplit('/', 2)[1]
    await download_ts(m3u8_url_link, folder_name)
    merge_ts(folder_name, output_name)


if __name__ == '__main__':
    asyncio.run(main())
