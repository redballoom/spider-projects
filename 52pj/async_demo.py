# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/17
📄File       : async_demo.py
ℹ️Description: 异步版本，只做补充学习用

- 实际运行只能获取5页，因为会报429的错误，需要设置代理。
- 我找不到免费的可用的代理，到此便不了了之。
- 代码注释采用的是vscode的插件（Baidu Comate）。
"""
import asyncio
import csv
import re
from urllib.parse import urljoin

from lxml import etree
import aiohttp
import aiofiles
from fake_useragent import UserAgent

base_url = 'https://www.52pojie.cn/'
fieldnames = ['album_title', 'album_url', 'album_rss', 'album_review', 'album_author', 'album_latest_time',
              'album_latest_topic']
save_file_name = 'async_demo.csv'


async def get_page(session, url):
    # 创建一个 UserAgent 对象
    ua = UserAgent()

    # 设置请求头
    headers = {
        # 接受的响应内容类型
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        # 连接类型，保持连接
        "Connection": "keep-alive",
        # 随机选择一个 User-Agent
        "User-Agent": ua.random,
    }

    try:
        # 发起 GET 请求
        async with session.get(url, headers=headers, timeout=10) as response:
            # 等待 1 秒
            await asyncio.sleep(1)
            # 检查响应状态码，如果异常则抛出异常
            response.raise_for_status()
            # 返回响应的文本内容
            return await response.text()
    except aiohttp.ClientError as err:
        # 打印 GET 请求错误
        print(f"Error making GET request to {url}: {err}")
        # 返回 None
        return None


async def get_index_page(session, page):
    # 构造页面URL
    page_url = f'https://www.52pojie.cn/forum.php?mod=collection&order=dateline&op=all&page={page}'
    # 异步调用get_page函数获取页面HTML数据
    html_data = await get_page(session, page_url)
    if html_data:
        # 打印当前解析的页码
        print(f'......开始解析第{page}页......')
        # 调用parse函数解析HTML数据并返回结果
        return parse(html_data)
    else:
        # 如果没有获取到HTML数据，则返回空列表
        return []


def parse(html):
    # 解析html字符串，生成HTML解析树
    tree = etree.HTML(html)
    # 查找所有class包含"clct_list"的div元素
    divs = tree.xpath('//div[contains(@class, "clct_list")]/div')
    # 用于存储解析结果的列表
    data_list = []

    # 遍历每个div元素
    for item in divs:
        # 提取专辑标题
        album_title = item.xpath('./dl/dt/div/a/text()')[0]
        # 提取专辑链接的href属性值
        album_href = item.xpath('./dl/dt/div/a/@href')[0]
        # 拼接完整的专辑链接
        album_url = urljoin(base_url, album_href)
        # 提取专辑信息中的文本内容
        album_info = item.xpath('./dl/dd[2]/p[2]/text()')[0]
        # 使用正则表达式提取专辑订阅数
        album_rss = re.search(r'订阅 (\d+)', album_info).group(1) if re.search(r'订阅 (\d+)', album_info) else ''
        # 使用正则表达式提取专辑评论数
        album_review = re.search(r'评论 (\d+)', album_info).group(1) if re.search(r'评论 (\d+)', album_info) else ''
        # 提取专辑作者
        album_author = item.xpath('./dl/dd[2]/p[3]/a/text()')[0]
        # 提取专辑更新时间
        album_update_time = item.xpath('./dl/dd[2]/p[3]/text()')[0]
        # 替换字符串中的"创建, 最后更新"为空字符串，得到专辑最新时间
        album_latest_time = re.sub('创建, 最后更新', '', album_update_time)
        # 提取专辑最新主题
        album_latest_topic = item.xpath('./dl/dd[2]/p[4]/a/text()')[0] if item.xpath('./dl/dd[2]/p[4]/a/text()') else ''

        # 将解析的专辑信息添加到data_list列表中
        data_list.append({
            'album_title': album_title,  # 专辑标题
            'album_url': album_url,  # 专辑链接
            'album_rss': album_rss,  # 专辑订阅
            'album_review': album_review,  # 专辑评论
            'album_author': album_author,  # 专辑作者
            'album_latest_time': album_latest_time,  # 专辑最新时间
            'album_latest_topic': album_latest_topic  # 专辑最新主题
        })

    return data_list


async def save_to_csv(lock, data):
    # 如果数据为空，则直接返回
    if not data:
        return

    # 异步获取锁
    async with lock:
        # 使用异步方式打开文件，并指定模式为追加、无换行符、编码为utf-8
        async with aiofiles.open('save_file_name', mode='a', newline='', encoding='utf-8') as f:
            # 创建csv.DictWriter对象，指定写入文件的字段名
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            # 遍历数据列表
            for row in data:
                # 将每行数据的值以逗号分隔，并添加换行符，然后写入文件
                await f.write(','.join(row.values()) + '\n')


async def main():
    # 创建一个异步锁
    lock = asyncio.Lock()

    # 创建一个异步HTTP客户端会话
    async with aiohttp.ClientSession() as session:
        # 创建一组异步任务，用于获取索引页面
        tasks = [get_index_page(session, i) for i in range(1, 11)]  # 10 组data_list数据
        # 等待所有任务完成，并获取页面数据
        pages_data = await asyncio.gather(*tasks)
        # 提取非空页面数据，并拼接成总数据列表
        total_data = [data for page_data in pages_data for data in page_data if page_data]

        # 初始化CSV，写入头部
        async with aiofiles.open('save_file_name', mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            await writer.writeheader()

        # 使用锁并发地写入数据
        await asyncio.gather(*(save_to_csv(lock, [data]) for data in total_data))

        print('保存完毕！')


if __name__ == '__main__':
    asyncio.run(main())


