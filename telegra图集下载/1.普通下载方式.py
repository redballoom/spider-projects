# #!/usr/bin/python3
# # -*- coding: utf-8 -*-
# import os
# from urllib.parse import urljoin
# import requests
# from bs4 import BeautifulSoup
#
# base_url = 'https://telegra.ph/'
# url = 'https://telegra.ph/%E8%8C%B6%E7%B1%BDccz--%E9%BE%99%E9%97%A8%E9%A3%9E%E5%A4%A9-113P-06-24'
#
# headers = {
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
# }
# r = requests.get(url, headers=headers)
#
# # print(r.text)
# # with open('test.html', 'w', encoding='utf-8') as f:
# #     f.write(r.text)
#
# with open('test.html', 'r', encoding='utf-8') as f:
#     html = f.read()
#
# soup = BeautifulSoup(html, 'lxml')
# title = soup.h1.string
#
# imgs = soup.find_all('img')
# for img in imgs:
#     img_src = img.get('src')
#     full_url = urljoin(base_url, img_src)
#     print(f'downloading... {full_url}')
#     req = requests.get(full_url, headers=headers)
#
#     folder = f'img/{title}'
#     file_name = full_url.rsplit('/', 1)[-1]
#     os.makedirs(folder, exist_ok=True)
#     path = os.path.join(folder, file_name)
#     with open(path, 'wb') as f:
#         f.write(req.content)
#
