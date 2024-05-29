# -*- coding: utf-8 -*-
"""
此代码来源是腾讯云的 云市场的图片验证码识别，官方提供的api接口太复杂，可读性极差，这是经过GPT优化的可读版本

若想使用，你需要到：https://market.cloud.tencent.com/products/21094 花1元购买api

提供:SECRET_ID 和 SECRET_KEY即可。
"""

import base64
import hmac
import hashlib
import requests
from datetime import datetime as pydatetime
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('user_config.ini')

# 云市场分配的密钥Id（建议使用环境变量或配置文件）
SECRET_ID = cfg.get('ORC', 'SECRET_ID')
SECRET_KEY = cfg.get('ORC', 'SECRET_KEY')
SOURCE = "market"
URL = 'http://service-98wvmcga-1256810135.ap-guangzhou.apigateway.myqcloud.com/release/yzm'


def get_authorization_header(secret_id, secret_key, source):
    datetime_str = pydatetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    sign_str = f"x-date: {datetime_str}\nx-source: {source}"
    sign = base64.b64encode(hmac.new(secret_key.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha1).digest())
    auth = f'hmac id="{secret_id}", algorithm="hmac-sha1", headers="x-date x-source", signature="{sign.decode("utf-8")}"'
    return {
        'X-Source': source,
        'X-Date': datetime_str,
        'Authorization': auth,
    }


def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


def recognize_captcha(image_path):
    # 获取授权头
    headers = get_authorization_header(SECRET_ID, SECRET_KEY, SOURCE)
    # 编码图片
    encoded_image = encode_image_to_base64(image_path)
    # 构建请求body
    body_params = {
        "number": "",
        "pri_id": "",
        "v_pic": encoded_image
    }
    # 发起POST请求
    response = requests.post(URL, headers=headers, data=body_params, verify=False)
    return response.json()['v_code']


if __name__ == "__main__":
    # 我们在if __name__ == "__main__"内的测试代码，在其他文件的调用中不会被使用。
    input_image_path = 'datas/7v0XZn2FQMq5Syo63Bxp.png'
    result = recognize_captcha(input_image_path)
    print(result)
