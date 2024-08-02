#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import asyncio
from urllib.parse import urljoin

from lxml import etree
import aiohttp
import aiofiles

proxy_url = "http://127.0.0.1:9910"  # Replace with your proxy address

"""完整版"""


async def get_page(url, retry=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    for attempt in range(1, retry + 1):
        try:
            async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url, proxy=proxy_url, timeout=60) as response:
                    response.raise_for_status()
                    return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Request failed, attempt {attempt}, error: {e}")
            await asyncio.sleep(attempt * 2)
    print("Reached maximum retry limit, returning None")
    return None


async def get_index_page(url):
    html_data = await get_page(url)
    if html_data:
        tree = etree.HTML(html_data)
        a_list = tree.xpath('//div[@class="module-play-list"]/div/a/@href')
        for a in a_list:
            play_url = urljoin('https://1anime.me/', a)
            yield play_url
    else:
        print("Failed to get index page data")


async def download_m3u8(url, folder_path):
    doc_html = await get_page(url)
    try:
        player_json = re.search(r'var player_aaaa=(.*?)</script>', doc_html, re.S).group(1)
        player_dict = json.loads(player_json)
        m3u8_url = player_dict['url']
        print(f'Get m3u8 url：{m3u8_url}')
        if m3u8_url.endswith('.m3u8'):
            m3u8_file_path = os.path.join(folder_path, m3u8_url.split('/')[-1])
            m3u8_data = await get_page(m3u8_url)
            async with aiofiles.open(m3u8_file_path, mode='w', encoding='utf-8') as f:
                await f.write(m3u8_data)
            return m3u8_url, m3u8_file_path
    except (AttributeError, json.JSONDecodeError) as e:
        print(f"Failed to parse player_json: {e}")
        return None


async def download_ts_line(session, ts_url, ts_path, semaphore, retry=5):
    async with semaphore:
        for attempt in range(1, retry + 1):
            try:
                async with session.get(ts_url, proxy=proxy_url, timeout=60) as response:
                    response.raise_for_status()
                    ts_content = await response.read()
                    await asyncio.sleep(1)
                    async with aiofiles.open(ts_path, 'wb') as f:
                        await f.write(ts_content)
                        await f.flush()
                    print(f'{ts_url} -- succeed!')
                    return  # Exit after successful download
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Failed to download {ts_url}, attempt {attempt}, error: {e}")
                await asyncio.sleep(attempt * 2)
        print(f"Reached maximum retry limit for {ts_url}, giving up")


async def download_ts(url, path, folder_path):
    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        lines = await f.readlines()

    tasks = []
    sem = asyncio.Semaphore(50)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        for line in lines:
            if line.startswith('#'):
                continue
            ts_url = url.rsplit('/', 1)[0] + '/' + line.strip()
            ts_path = os.path.join(folder_path, line.strip())
            tasks.append(download_ts_line(session, ts_url, ts_path, sem))
        await asyncio.gather(*tasks)


def merge_ts(folder, output):
    merge_folder = 'merge'
    if not os.path.exists(merge_folder):
        os.mkdir(merge_folder)

    index_m3u8_path = os.path.join(folder, 'master.m3u8')
    output_path = os.path.join(merge_folder, f'{output}.mp4')  # 合并后的视频目录
    cmd = f'ffmpeg -i "{index_m3u8_path}" -c copy "{output_path}"'
    os.system(cmd)
    print(f'{output_path} -- merge complete!')

    for file in os.listdir(folder):
        if file.endswith(".ts"):
            os.remove(os.path.join(folder, file))


async def main():
    index_url = 'https://1anime.me/voddetail/8183.html'  # 替换url下载不同的动漫
    ts_folder = 'ts'
    if not os.path.exists(ts_folder):
        os.mkdir(ts_folder)

    playlist = get_index_page(index_url)

    async for url in playlist:
        print(f'Starting... {url}')
        output = re.search(r'(\d-\d+)', url).group(1)
        m3u8_result = await download_m3u8(url, ts_folder)

        m3u8_url, m3u8_path = m3u8_result
        if os.path.exists(m3u8_path):
            await download_ts(m3u8_url, m3u8_path, ts_folder)
            merge_ts(ts_folder, output)
        else:
            print("Failed to download m3u8 file")


if __name__ == '__main__':
    asyncio.run(main())
