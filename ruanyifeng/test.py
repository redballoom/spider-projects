# -*- coding:utf-8 -*-
"""
✍️Author     : 🎈
⏲️Time       : 2024/5/22
📄File       : test.py
ℹ️Description: 简短描述该文件的主要功能或目的

"""
import unittest
from pyquery import PyQuery
from new_demo import detail_parse_page


def read_html_file(file_name):
    with open(file_name, 'r', encoding='utf') as f:
        data = f.read()
    return data


class TestDetailParsePage(unittest.TestCase):
    """测试解析网页数据和返回数据是否相同"""
    def test_parse_valid_html(self):
        detail_html = read_html_file('html/weekly-issue-300.html')
        expected_output = [{'title': 'LaTeX 入门与进阶', 'href': 'https://latex.lierhua.top/zh/',
                            'desc': ' 网友写的中文书籍，介绍如何使用 LaTeX 和宏包编写。（@immotal 投稿）',
                            'img': 'https://cdn.beekka.com/blogimg/asset/202405/bg2024051107.webp'},
                           {'title': 'URLhaus 数据库', 'href': 'https://urlhaus.abuse.ch/browse/',
                            'desc': ' 这个数据库专门收集各种恶意 URL 网址，目前已经收集了280万个，可以免费查询和下载。',
                            'img': 'https://cdn.beekka.com/blogimg/asset/202405/bg2024051503.webp'},
                           {'title': '数据科学导论', 'href': 'https://rafalab.dfci.harvard.edu/dsbook-part-1/',
                            'desc': ' 开源的英文教材，源于哈佛大学同名课程，使用 R 语言学习数据科学。',
                            'img': 'https://cdn.beekka.com/blogimg/asset/202403/bg2024030201.webp'},
                           {'title': '引脚定义', 'href': 'https://pinouts.org/',
                            'desc': ' 一本免费英文电子书，收集了130种电子产品常见组件（比如 USB 口）的引脚定义。',
                            'img': 'https://cdn.beekka.com/blogimg/asset/202309/bg2023091204.webp'}, ]
        self.assertEqual(detail_parse_page(detail_html), expected_output)


if __name__ == '__main__':
    unittest.main()
