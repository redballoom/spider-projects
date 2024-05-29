# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : n02-使用Base64编码的图片爬取与解码还原.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/n02/
"""
# 导入需要的库
import base64
import os

import requests
from lxml import etree

save_directory = 'datas'
os.makedirs(save_directory, exist_ok=True)  # exist_ok=True 如果目录已经存在，则不引发错误, False则反之


def get_page(url, headers=None):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=default_headers, timeout=10)
        response.raise_for_status()  # 如果不是2XX状态码请求，则抛出HTTPError错误
        return response
    except requests.exceptions.RequestException as e:  # 通用requests异常捕获
        print(f"Error making request to {url}: {e}")
        return None


def lxml_parse(html):
    dom = etree.HTML(html)
    img = dom.xpath('//img/@src')[0]
    base64_data = img.replace('data:image/png;base64,', '')  # 替换掉不需要的内容，后面的才是经过base64编码的二进制数据
    img_content = base64.b64decode(base64_data)  # base64解码为二进制数据
    return img_content


def save_data(data, file_name='base64.png'):
    """数据保存
    :param data: 图片的二进制数据
    :param file_name: 图片名称
    """
    path = os.path.join(save_directory, file_name)
    with open(path, mode='wb') as f:
        f.write(data)


def main():
    url = 'http://www.spiderbuf.cn/n02/'
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
        'Referer': 'http://www.spiderbuf.cn/list'
    }
    html_text = get_page(url, headers=my_headers)
    if html_text:
        img_content = lxml_parse(html_text)
        save_data(img_content)
        print('All Done!')


if __name__ == '__main__':
    main()
