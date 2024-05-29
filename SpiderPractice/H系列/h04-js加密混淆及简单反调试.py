# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月31
@ 📄File       : h04-js加密混淆及简单反调试.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/h04/

其实就跟ajax一样，找到对应的数据接口即可，不过这是在js文件中

步骤：
    - 对于debugger，可以右键一律不在此展厅或设置条件过掉，但这也治标不治本，一劳永逸的方法是HOOK debugger的断点位置，这需要自行去学习。
    - 刷新网页后看到我们的doc文件中没有我们需要的数据，此时可断定它是动态加载的数据，就要去找其数据加载的位置或文件、接口
    - ctrl + f 直接搜索密码的数据，能看到一个js文件，其中就包含数据信息，只需要获取下来即可。

对于js文件，我们先前一直使用的xpath解析就无能为力了，re库就可以帮助我们从js代码中提取需要的信息。
"""
import os
import csv
from time import sleep
import re
import json

import requests

FOLDER_NAME = 'datas'
os.makedirs(FOLDER_NAME, exist_ok=True)


def get_page(url, headers=None, retries=3):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()  # 如果不是200状态码请求，则抛出HTTPError错误
            return response.text
        except requests.exceptions.RequestException as e:  # 通用异常捕获
            print(f"Error making request to {url}: {e}. Attempt {attempt + 1} of {retries}.")
            sleep(2 ** attempt)  # 指数退避策略
    return None


def json_to_dict(json_str):
    # 先进行Unicode转义解码
    json_data = json_str.encode('utf-8').decode('unicode_escape').replace('\'', '"')
    # 将十六进制数替换为十进制数
    json_data = re.sub(r'0x[0-9a-fA-F]+', lambda x: str(int(x.group(0), 16)), json_data)
    json_data = json.loads(json_data)  # 转换为标准json格式，避免出现错误
    return json_data


def parse_data(js_data):
    pattern = re.compile(r'data=(.*?);', re.S)
    json_data = re.search(pattern, js_data).group(1)  # json数据
    json_to_dict(json_data)
    dict_data = json_to_dict(json_data)

    dict_list = []
    for item in dict_data:
        dit = {
            'ranking': item['ranking'],
            'password': item['passwd'],
            'cracking_time': item['time_to_crack_it'],
            'use_num': item['used_count'],
        }
        dict_list.append(dit)
    return dict_list


def save_data(datas, file_name='h04-全球最常用密码列表.csv'):
    """数据保存"""
    save_directory = 'datas'
    os.makedirs(save_directory, exist_ok=True)  # exist_ok=True 如果目录已经存在，则不引发错误, False则反之

    fieldnames = ['ranking', 'password', 'cracking_time', 'use_num']
    path = os.path.join(save_directory, file_name)  # 完整文件路径
    file_exists = os.path.exists(path)
    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(datas)


def main():
    js_url = 'http://spiderbuf.cn/static/js/h04/udSL29.js'
    js_data = get_page(js_url)
    if js_data:
        dict_data = parse_data(js_data)
        save_data(dict_data)

    # decoded_data = eval(json_data)
    # print(decoded_data)
    # for item in decoded_data:
    #     print(item)


if __name__ == '__main__':
    main()
