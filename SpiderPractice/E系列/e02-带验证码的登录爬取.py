# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/23
📄File       : e02-带验证码的登录爬取.py
ℹ️Description: 简短描述该文件的主要功能或目的

练习目标：http://www.spiderbuf.cn/e02/

"""
# 导入需要的库
import os.path
from urllib.parse import urljoin
from orc_code import recognize_captcha  # 验证码识别的文件

import requests
from lxml import etree


base_url = 'http://www.spiderbuf.cn/e02/'

# 在做登录页面时，通常采用session的请求方式，这样的好处是可以保持HTTP的请求状态。
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})


def get_page(url, data=None, **kwargs):
    try:
        response = session.post(url, data=data, timeout=10, **kwargs)
        response.raise_for_status()  # 如果不是2xx状态码请求，则抛出HTTPError错误
        return response.text  # 返回响应对象
    except requests.exceptions.RequestException as e:  # 通用异常捕获
        print(f"Error making request to {url}: {e}")
        return None


def save_code_img(login_html):
    """保存验证码图片，静态网页直接取验证码图片链接"""
    doc = etree.HTML(login_html)
    code_img_url = doc.xpath('//img[@id="image"]/@src')[0]
    code_img = urljoin(base_url, code_img_url)

    img_content = requests.get(code_img).content
    img_name = code_img.split('/')[-1]
    img_path = os.path.join('datas/', img_name)
    print(f'保存验证码图片：{img_path}')
    with open(img_path, 'wb') as f:
        f.write(img_content)
    return img_name, img_path


def login_data(name, path):
    """构造post请求的参数"""
    result = recognize_captcha(path)
    img_name = name.replace('.png', '')
    data = {
        'username': 'admin',
        'password': '123456',
        'captchaSolution': result,
        'captchaId': img_name,
    }
    print(data)
    return data


def parse(html):
    """
    解析数据
    :param html: 网页的源代码
    :return: None
    """
    dom_tree = etree.HTML(html)
    # tr元素，一共50条
    trs = dom_tree.xpath('//table[@class="table"]/tbody/tr')
    page_data = []
    for tr in trs:
        ranking = tr.xpath('./td[1]/text()')[0]
        value = tr.xpath('./td[2]/text()')[0]
        enterprise_information = tr.xpath('./td[3]/text()')[0]
        ceo_name = tr.xpath('./td[4]/text()')[0]
        profession = tr.xpath('./td[5]/text()')[0]
        row_data = ','.join([ranking, value, enterprise_information, ceo_name, profession, '\n'])
        page_data.append(row_data)
    # 保存文件
    save_data(page_data)


def save_data(data_list, file_name='e02胡润中国500强.txt'):
    """数据保存"""
    folder_name = 'datas'
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    path = os.path.join(folder_name, file_name)  # 完整文件路径
    with open(path, mode='w', encoding='utf-8') as f:
        f.writelines(data_list)


def main():
    try:
        login_response = session.get(base_url)  # 获取验证码图片所在网页的源代码
        img_code_name, img_code_path = save_code_img(login_response.text)
        data = login_data(img_code_name, img_code_path)  # 构造post请求携带参数

        login_url = 'http://www.spiderbuf.cn/e02/login'  # 真正登录的链接
        login_html = get_page(login_url, data)
        if login_html:
            parse(login_html)
    except Exception as e:
        print(f"Main function encountered an error: {e}")


if __name__ == '__main__':
    main()
