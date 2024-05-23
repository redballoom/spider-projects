# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/19
📄File       : new_jijian.py
ℹ️Description: 爬取极简壁纸的壁纸，更优雅的实现方法

"""
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

import requests
from loguru import logger
import execjs


def general_request(method, url, headers=None, **kwargs):
    """真正的通用请求方法。

    :param method: 请求方式 [``GET``, ``POST`` ......]
    :param url: 请求地址
    :param headers: 请求头
    :return: response响应对象
    """
    default_headers = headers or {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    }

    try:
        response = requests.request(method, url, headers=default_headers, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during request: {e}")
        return None


def generate_api_data(page):
    """根据page页码生成自定义的数据载荷信息，以供POST请求时携带"""
    return {"size": 24, "current": page, "sort": 0, "category": 0,
            "resolution": 0, "color": 0, "categoryId": 0, "ratio": 0}


def decrypt_result(data):
    """
    使用 JavaScript 代码对结果进行解密。

    :param data: 包含加密数据的字典数据.
    :return: 如果成功解密，则为解密后的数据，否则为None。
    """
    try:
        result = data['result']  # 加密的数据
        with open('new_jijian.js', mode='r', encoding='utf-8') as f:
            js_code = f.read()
        # 使用execjs库编译JavaScript代码并通过decrypt_code函数执行解密
        json_data = execjs.compile(js_code).call('decrypt_code', result)
        data = json.loads(json_data)
        return data
    except Exception as e:
        logger.error(f"An error occurred during decryption: {e}")
        return None


def download_image(pic_url, pic_id, download_dir="images2"):
    """
    从给定的 pic_url 下载图片，并以给定的 pic_id 保存。

    :param pic_url: 下载图像的url
    :param pic_id: 保存图像的名称
    :param download_dir: 保存图像的目录。
    :return:
    """
    headers = {
        "Referer": "https://bz.zzzmh.cn/",  # 403 防盗链处理
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    try:
        os.makedirs(download_dir, exist_ok=True)  # 目录存在时不引发报错
        response = general_request('GET', pic_url, headers=headers, stream=True)  # 开启分块请求
        if response:
            img_file_path = os.path.join(download_dir, f"{pic_id}.jpg")
            # 打开文件，按块写入以节省内存
            with open(img_file_path, 'wb') as f:
                for chunk in response.iter_content(1024 * 512):  # 设置一块 ≈ 0.5 MB
                    f.write(chunk)
            logger.info(f"Downloaded image {pic_id} from {pic_url}")
        else:
            logger.error(f"Failed to download image {pic_id} from {pic_url}: {response.status_code}")
    except Exception as e:
        logger.error(f"An error occurred during downloading image {pic_id}: {e}")


def parse(data, download_queue):
    """
    从解密后的数据中解析出构成图片链接的参数，再拼接出完整图片链接，并放入下载队列。

    :param data: 要解析的数据
    :param download_queue: 用于保存下载任务的队列
    :return:
    """
    try:
        for item in data['list']:
            pic_id = item.get('i')
            pic_t = item.get('t')
            # 构建完整的壁纸下载链接
            pic_url = f'https://api.zzzmh.cn/bz/v3/getUrl/{pic_id}{pic_t}9'
            # 将下载任务添加到队列中
            download_queue.put((pic_url, pic_id))
    except Exception as e:
        logger.error(f"An error occurred during parsing: {e}")


def download_worker(download_queue):
    """
    工作函数，用于从下载队列中取任务并下载图片。

    :param download_queue: 保存下载任务的队列
    """
    while not download_queue.empty():
        try:
            pic_url, pic_id = download_queue.get()
            download_image(pic_url, pic_id)
            # 告知队列此任务已完成
            download_queue.task_done()
        except download_queue.Empty:
            break


def main():
    download_queue = Queue()  # 初始化队列
    api_url = "https://api.zzzmh.cn/bz/v3/getData"

    for page in range(1, 2):  # 1页的图片
        data_args = generate_api_data(page)
        page_response = general_request('POST', api_url, json=data_args, timeout=10)  # 接口的响应对象
        if page_response:
            decrypt_data = decrypt_result(page_response.json())
            if decrypt_data:  # 如果有解密数据
                parse(decrypt_data, download_queue)
            else:
                logger.info("decrypt_data is None. 注意你可能被反爬限制了!")

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(download_worker, download_queue) for _ in range(6)]

        for future in as_completed(futures):
            future.result()  # 等待所有线程完成
    download_queue.join()  # 等待队列中的所有任务完成


if __name__ == '__main__':
    s = time.time()
    main()
    print(f'耗时 {time.time() - s}')  # 耗时 89.2294065952301
