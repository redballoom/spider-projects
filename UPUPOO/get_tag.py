# -*- coding: utf-8 -*-
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2024年01月01
@ 📄File       : get_tag.py
@ ℹ️Description:

获取标签信息，可改变TAG_ID来实现更多选择的采集
"""
import requests

tag_url = 'https://pcwallpaper.upupoo.com/wallpaper/getTags'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) upupoo-wallpaper-shop/0.0.1 Chrome/80.0.3987.165 Electron/8.2.5 Safari/537.36',
}
response = requests.get(tag_url, headers=headers)
json_data = response.json()

cards = json_data['data']
print(len(cards))

f = open('tags.txt', 'a', encoding='utf-8')
for info in cards:
    tag_id = info['tag_id']
    tag_name = info['tag_name']
    tag_data = f'【{tag_id}】---【{tag_name}】'
    f.write(tag_data + '\n')
f.close()
