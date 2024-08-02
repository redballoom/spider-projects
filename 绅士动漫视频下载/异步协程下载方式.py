# #!/usr/bin/python3
# # -*- coding: utf-8 -*-
#
# import os
# import re
# import time
# import json
# import asyncio
# from urllib.parse import urljoin
#
# from lxml import etree
# import aiohttp
# import aiofiles
#
# """经过GPT优化后的版本"""
# proxy_url = "http://127.0.0.1:9910"  # 替换为您的代理地址
#
#
# async def get_page(url, retry=5):
#     """
#     通用请求方法，用于发起GET请求并返回页面内容。
#
#     :param url: 请求视频的URL。
#     :param retry: 请求重试的最大次数，默认值为3次。
#     :return: 返回请求页面的文本内容，如果失败则返回None。
#     """
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
#     }
#     i = 1
#     while i <= retry:
#         try:
#             async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
#                 async with session.get(url, proxy=proxy_url, timeout=60) as response:
#                     response.raise_for_status()
#                     return await response.text()
#         except aiohttp.ClientError as e:
#             print(f"请求失败，尝试次数：{i}, 错误信息：{e}")
#             await asyncio.sleep(i * 2)
#             i += 1
#     print("达到最大重试次数，返回 None")
#     return None
#
#
# async def get_index_page(url):
#     """
#     通过下载索引页的数据，提取出当前动漫所包含的所有集的url
#     :param url: 索引页url
#     :return: 动漫集数链接的生成器
#     """
#     html_data = await get_page(url)
#     if html_data:
#         tree = etree.HTML(html_data)
#         a_list = tree.xpath('//div[@class="module-play-list"]/div/a/@href')
#         for a in a_list:
#             play_url = urljoin('https://1anime.me/', a)
#             yield play_url
#     else:
#         print("未能获取到索引页数据")
#
#
# async def download_m3u8(url, folder_path):
#     """
#     根据生成器返回的集数链接，下载对应m3u8文件
#     :param url: 集数链接
#     :param folder_path: 保存m3u8文件的文件夹路径
#     :return: 下载的m3u8文件路径
#     """
#     doc_html = await get_page(url)
#     try:
#         player_json = re.search(r'var player_aaaa=(.*?)</script>', doc_html, re.S).group(1)
#         player_dict = json.loads(player_json)
#         m3u8_url = player_dict['url']
#         if m3u8_url.endswith('.m3u8'):
#             m3u8_file_path = os.path.join(folder_path, m3u8_url.split('/')[-1])
#             m3u8_data = await get_page(m3u8_url)
#             async with aiofiles.open(m3u8_file_path, mode='w', encoding='utf-8') as f:
#                 await f.write(m3u8_data)
#             return m3u8_url, m3u8_file_path
#     except (AttributeError, json.JSONDecodeError) as e:
#         print(f"解析player_json失败: {e}")
#         return None
#
#
# async def download_ts_line(session, ts_url, ts_path, semaphore):
#     """
#     下载单个ts文件并保存到指定路径。
#
#     :param session: aiohttp会话对象。
#     :param ts_url: ts文件的URL。
#     :param ts_path: 保存ts文件的路径。
#     """
#     async with semaphore:
#         async with session.get(ts_url, proxy=proxy_url, timeout=60) as response:
#             ts_content = await response.read()
#             await asyncio.sleep(1)
#         async with aiofiles.open(ts_path, 'wb') as f:
#             await f.write(ts_content)
#             await f.flush()
#         print(f'{ts_url} -- succeed!')
#
#
# async def download_ts(url, path, folder_path):
#     """
#     下载m3u8文件中的所有ts文件
#     :param path: m3u8文件路径
#     :param folder_path: 保存ts文件的文件夹路径
#     """
#     async with aiofiles.open(path, 'r', encoding='utf-8') as f:
#         lines = await f.readlines()
#
#     tasks = []
#     # 创建信号量 并发下载
#     sem = asyncio.Semaphore(50)
#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
#         for line in lines:
#             if line.startswith('#'):
#                 continue
#             else:
#                 api_path = url.rsplit('/', 1)[0]
#                 ts_url = api_path + '/' + line.strip()
#                 print(f'{ts_url} -- downloading...')
#                 ts_path = os.path.join(folder_path, line.strip())
#
#                 tasks.append(download_ts_line(session, ts_url, ts_path, sem))
#         await asyncio.gather(*tasks)
#
#
# def merge_ts(folder, output):
#     """
#     合并ts文件为MP4文件，并删除原始的ts文件。
#
#     :param folder: ts文件的文件夹路径。
#     :param output: 合并后输出的MP4文件名。
#     """
#     index_m3u8_path = os.path.join(folder, 'index.m3u8')
#     output = os.path.join(output)
#     cmd = rf'ffmpeg -i {index_m3u8_path} -c copy {output}.mp4'
#     os.system(cmd)
#     print(f'{output}.mp4 -- merge complete!')
#
#     # 删除TS文件
#     for file in os.listdir(folder):
#         if file.endswith(".ts"):
#             os.remove(os.path.join(folder, file))
#
#
# async def main():
#     index_url = 'https://1anime.me/voddetail/8183.html'
#     ts_folder = 'ts'
#     if not os.path.exists(ts_folder):
#         os.mkdir(ts_folder)
#
#     playlist = get_index_page(index_url)  # 动漫集数链接的生成器
#
#     async for url in playlist:
#         output = re.search(r'(-\d-\d+)', url).group(1)
#         m3u8_url, m3u8_path = await download_m3u8(url, ts_folder)
#         if os.path.exists(m3u8_path):
#             await download_ts(m3u8_url, m3u8_path, ts_folder)
#             merge_ts(ts_folder, output)
#         else:
#             print("未能下载m3u8文件")
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
