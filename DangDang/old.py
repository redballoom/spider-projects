# _*_ coding: utf-8 _*_
"""
@ 😀Author     : 🎈
@ ⏲️Time       : 2023年12月03
@ 📄File       : old.py
@ ℹ️Description:
采集当当网电子书 科技分类下的计算机/网络的数据

##################################################################################
# start和end是变化的，其实就是count数量,即一次请求返回的数据量，只要构造好并在请求时自动传参即可
# start 和 end 的规律：
# start  0  21 42 63  ...   计算公式: start = [i*20+i for i in range(0, you_need_page)]
# end    20 41 62 83  ...   计算公式: end = [20*i+20+i for i in range(0, you_need_page)]
##################################################################################
"""
import requests
import pymysql

you_need_page = 3
category = 'JSJWL'  # 这个参数控制分类，是分类名的缩写 （计算机/网络）
session = requests.Session()
session.headers.update({
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "e.dangdang.com",
    "Referer": "https://e.dangdang.com/list-JSJWL-comment-0-1.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
})  # 设置session 对象中的全局请求头

# 数据库连接配置
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'xxxxxxxx',
    'database': 'pyspider',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
# 创建数据库连接
connection = pymysql.connect(**db_config)


def get_api(url, params=None):
    """通用请求方法"""
    try:
        response = session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print(e)


def get_page_index(start, end):
    """
    控制翻页，通过动态传参构造好params请求参数
    :return:
    """
    url = 'https://e.dangdang.com/media/api.go'
    params = {
        "action": "mediaCategoryLeaf",
        "promotionType": "1",
        "deviceSerialNo": "html5",
        "macAddr": "html5",
        "channelType": "html5",
        "permanentId": "20231203171009072205756652120872036",
        "returnType": "json",
        "channelId": "70000",
        "clientVersionNo": "6.8.0",
        "platformSource": "DDDS-P",
        "fromPlatform": "106",
        "deviceType": "pconline",
        "token": "",
        "start": "{}".format(start),
        "end": "{}".format(end),
        "category": category,
        "dimension": "comment",
        "order": "0"
    }
    return get_api(url, params=params)


def parse(json_data):
    """解析数据"""
    data_lists = json_data['data']['saleList']
    for data in data_lists:
        title = data['mediaList'][0]['title']
        author = data['mediaList'][0]['authorPenname']
        price = data['mediaList'][0]['salePrice']
        category = data['mediaList'][0]['categorys']
        descs = data['mediaList'][0]['descs']

        # 保存到数据库
        save_to_database(title, author, price, category, descs)
        print("====== Successful！ ======")
        # print(title, author, price, category, "Saved to database", sep=' | ')


def create_table():
    try:
        with connection.cursor() as cursor:
            # 创建表的 SQL 语句
            sql = """CREATE TABLE IF NOT EXISTS dangdangwang (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                author VARCHAR(255),
                price DECIMAL(10, 2),
                category VARCHAR(255),
                descs TEXT
            )"""
            cursor.execute(sql)

        # 提交事务
        connection.commit()
    except Exception as e:
        # 发生错误时回滚
        print(f"Error creating table: {e}")
        connection.rollback()


def save_to_database(title, author, price, category, descs):
    try:
        with connection.cursor() as cursor:
            # 执行插入数据的 SQL 语句
            sql = "INSERT INTO dangdangwang (title, author, price, category, descs) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (title, author, price, category, descs))

        # 提交事务
        connection.commit()
    except Exception as e:
        # 发生错误时回滚
        print(f"Error saving to database: {e}")
        connection.rollback()


def run():
    # 构造params的start和end参数 [(s, e),(...),...]
    data = [(i * 20 + i, 20 * i + 20 + i) for i in range(0, you_need_page)]
    for k, v in data:
        json_data = get_page_index(k, v)
        parse(json_data)


if __name__ == '__main__':
    create_table()
    run()
