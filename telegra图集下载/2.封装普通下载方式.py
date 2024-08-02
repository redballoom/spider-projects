# #!/usr/bin/python3
# # -*- coding: utf-8 -*-
# import os
# import logging
# import time
# from urllib.parse import urljoin
#
# import requests
# from bs4 import BeautifulSoup
#
# # Constants
# BASE_URL = 'https://telegra.ph/'
# PAGE_URL = 'https://telegra.ph/%E8%8C%B6%E7%B1%BDccz--%E9%BE%99%E9%97%A8%E9%A3%9E%E5%A4%A9-113P-06-24'
# HEADERS = {
#     "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                    "AppleWebKit/537.36 (KHTML, like Gecko) "
#                    "Chrome/127.0.0.0 Safari/537.36")
# }
# RETRY_LIMIT = 5  # 最大重试数
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
#
# def get_page(url):
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=15)
#         response.raise_for_status()
#         return response.text
#     except requests.exceptions.RequestException as e:
#         logger.error(f'Error fetching page: {e}')
#         return None
#
#
# def parse_page(html):
#     soup = BeautifulSoup(html, 'lxml')
#     title = soup.h1.string.strip()
#     imgs = soup.find_all('img')
#     img_data_list = [urljoin(BASE_URL, img.get('src')) for img in imgs]
#     return {'title': title, 'img_src_list': img_data_list}
#
#
# def save_data(data, folder_name, file_name):
#     folder_path = os.path.join(f'img/{folder_name}')
#     os.makedirs(folder_path, exist_ok=True)
#     path = os.path.join(folder_path, file_name)
#     with open(path, 'wb') as file:
#         file.write(data)
#
#
# def download_img(url, folder_name, retry=RETRY_LIMIT):
#     for attempt in range(1, retry + 1):
#         try:
#             response = requests.get(url, timeout=15)
#             response.raise_for_status()
#             save_data(response.content, folder_name, url.rsplit('/', 1)[-1])
#             logger.info(f'Successfully downloaded {url}')
#             break
#         except requests.exceptions.RequestException as e:
#             logger.warning(f'Attempt {attempt} for {url} failed: {e}')
#             time.sleep(attempt * 2)
#             if attempt == retry:
#                 logger.error(f'Failed to download {url} after {retry} attempts')
#
#
# if __name__ == '__main__':
#     html_data = get_page(PAGE_URL)
#     if html_data:
#         result_data = parse_page(html_data)
#         folder = result_data['title']
#         for src_url in result_data['img_src_list']:
#             download_img(src_url, folder)
#     else:
#         logger.error('Failed to retrieve the HTML content')
