#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from loguru import logger
import asyncio
from urllib.parse import urljoin

import aiohttp
import aiofiles
from bs4 import BeautifulSoup

# Constants
BASE_URL = 'https://telegra.ph/'
PAGE_URL = 'https://telegra.ph/%E8%8C%B6%E7%B1%BDccz--%E9%BE%99%E9%97%A8%E9%A3%9E%E5%A4%A9-113P-06-24'
HEADERS = {
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/127.0.0.0 Safari/537.36")
}
RETRY_LIMIT = 5  # 最大重试数
PROXY = 'http://127.0.0.1:9910'  # 添加代理访问


async def get_page(url):
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, proxy=PROXY) as response:
                response.raise_for_status()
                return await response.text()
    except aiohttp.ClientError as e:
        logger.error(f'Error fetching page: {e}')
        return None


def parse_page(html):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.h1.string.strip()
    imgs = soup.find_all('img')
    img_data_list = [urljoin(BASE_URL, img.get('src')) for img in imgs]
    return {'title': title, 'img_src_list': img_data_list}


async def save_data(data, folder_name, file_name):
    folder_path = os.path.join(f'img/{folder_name}')
    os.makedirs(folder_path, exist_ok=True)
    path = os.path.join(folder_path, file_name)
    async with aiofiles.open(path, 'wb') as file:
        await file.write(data)


async def download_img(session, url, folder_name, retry=RETRY_LIMIT):
    file_name = url.rsplit('/', 1)[-1]
    for attempt in range(1, retry + 1):
        try:
            async with session.get(url, proxy=PROXY, timeout=60) as response:
                response.raise_for_status()
                content = await response.read()
                await save_data(content, folder_name, file_name)
            logger.info(f'Successfully downloaded {url}')
            break
        except aiohttp.ClientError as e:
            logger.warning(f'Attempt {attempt} for {url} failed: {e}')
            if attempt == retry:
                logger.error(f'Failed to download {url} after {retry} attempts')
            await asyncio.sleep(attempt * 2)


async def main():
    html_data = await get_page(PAGE_URL)
    if html_data:
        result_data = parse_page(html_data)
        folder = result_data['title']
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            tasks = [download_img(session, src_url, folder) for src_url in result_data['img_src_list']]
            await asyncio.gather(*tasks)
    else:
        logger.error('Failed to retrieve the HTML content')


if __name__ == '__main__':
    asyncio.run(main())
