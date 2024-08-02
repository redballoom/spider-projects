#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os


# "https:\/\/cdn.s3.6782563.xyz\/vod\/hdb\/70302\/data\/01_cykfihd9pi\/master.m3u8"
# "https://us.s3.877654.xyz/vod/hdb/70302/data/01_cykfihd9pi/master.m3u8"
# "https://cdn.s3.6782563.xyz/vod/hdb/70302/data/01_cykfihd9pi/master.m3u8"
# """下载一个动漫的多集，测试只下载一集"""

# ts_url = 'https://cdn.s3.6782563.xyz/vod/hdb/70302/data/01_cykfihd9pi/'
# api_path = ts_url.split('/')[3:-1]
# api_path = '/'.join(api_path)
# print(api_path)

def merge_ts(folder, output):
    index_m3u8_path = os.path.join(folder, 'master.m3u8')
    output_path = os.path.join(f'{output}.mp4')
    cmd = f'ffmpeg -i "{index_m3u8_path}" -c copy "{output_path}"'
    os.system(cmd)
    print(f'{output_path} -- merge complete!')


merge_ts('ts', 'output')
