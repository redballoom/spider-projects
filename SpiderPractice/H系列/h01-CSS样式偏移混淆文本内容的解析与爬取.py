# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月30
@ 📄File       : h01-CSS样式偏移混淆文本内容的解析与爬取.py
@ ℹ️Description:
练习目标：http://www.spiderbuf.cn/h01/

处理css字符偏移的反爬案例
"""

# 导入需要的库
import os
import requests
import csv
from lxml import etree


def get_page(url, headers=None, retries=3):
    default_headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    for _ in range(retries):
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()  # 如果不是200状态码请求，则抛出HTTPError错误
            return response.text
        except requests.exceptions.RequestException as e:  # 通用异常捕获
            print(f"Error making request to {url}: {e}")
    return None


def lxml_parse(html):
    """
    使用 lxml 的 etree 解析 HTML
    :param html: 一页的网页源代码数据
    :return page_data_list: 解析后的一页字典数据列表
    """

    # <div class="col-xs-6 col-lg-4" style="margin-bottom: 30px;">
    #         <h2><i style="width: 32px;position: relative; left: 32px;">节</i><i style="width: 32px;position: relative; left: -32px;">字</i><i style="width: 32px;position: relative;">跳</i><i style="width: 32px;position: relative;">动</i></h2>
    #         <p>排名：4</p>
    #         <p>企业估值(亿元)：<i style="width: 14px;position: relative; left: 10px;">2</i><i style="width: 14px;position: relative; left: -10px;">2</i><i style="width: 14px;position: relative;">5</i><i style="width: 14px;position: relative;">0</i></p>
    #         <p>CEO：张利东</p>
    #         <p>行业：传媒和娱乐</p>
    #     </div><!--/.col-xs-6.col-lg-4-->
    # 找到对应字符的偏移（交换）的规律，在python中解析出字符串后交换位置即可
    page_data_list = []
    dom_tree = etree.HTML(html)
    divs = dom_tree.xpath('//div[@class="container"]/div/div')
    for div in divs:
        title = div.xpath('./h2//text()')
        title[0], title[1] = title[1], title[0]  # 交换下标0和1的值, 其实就是交换偏移的值
        company_name = ''.join(title)

        ranking = div.xpath('./p[1]/text()')[0].replace('排名：', '')

        value = div.xpath('./p[2]//text()')[1:]
        value[0], value[1] = value[1], value[0]
        company_value = ''.join(value)

        ceo_name = div.xpath('./p[3]/text()')[0].replace('CEO：', '')
        profession = div.xpath('./p[4]/text()')[0].replace('行业：', '')
        dic = {'企业': company_name,
               '排名': ranking,
               '企业估值(亿元)': company_value,
               'CEO': ceo_name,
               '行业': profession, }
        page_data_list.append(dic)
    return page_data_list


def save_data(datas, file_name='h01胡润中国500强.csv'):
    """数据保存"""
    save_directory = 'datas'
    os.makedirs(save_directory, exist_ok=True)  # exist_ok=True 如果目录已经存在，则不引发错误, False则反之

    csv_header = ['企业', '排名', '企业估值(亿元)', 'CEO', '行业']
    path = os.path.join(save_directory, file_name)
    write_header = not os.path.exists(path)  # 如果路径不存在，我们才写入csv_header
    with open(path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_header)
        if write_header:  # 根据 write_header 的判断，确保只会写一次头信息
            writer.writeheader()
        writer.writerows(datas)


def main():
    url = 'http://www.spiderbuf.cn/h01/'
    html_data = get_page(url)
    if html_data:
        data_list = lxml_parse(html_data)
        save_data(data_list)
    print('All Done!')


if __name__ == '__main__':
    main()
