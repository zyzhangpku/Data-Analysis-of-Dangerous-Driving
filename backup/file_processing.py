# coding: utf-8

"""
本程序的目的是从下载的1300个文书中提取变量。
为方便后续的处理，提取的变量将被储存至files文件中的data.csv中。
后续的数据处理工作将直接读取data.csv。
"""

import os
import csv
from settings import *

# 读取文件目录
files = os.listdir('./files/')


class Judgement:
    """表示判决文书的类"""

    def __init__(self, filepath):
        self.filepath = './files/' + filepath
        if self.judge():
            self.output()

    def judge(self):
        """判断该文件是否为一审刑事判决书"""

        with open(self.filepath, encoding='utf-8') as f:
            f.readline()
            f.readline()
            if '一审刑事判决书' in f.readline():
                return True
            else:
                return False

    def find_variables(self):
        """从文书中提取变量"""

        with open(self.filepath, encoding='utf-8') as f:
            text = f.read()

            filename = self.filepath[8:]  # 文件名称
            website = extract(text, 'https:.*?.html')  # 源网站
            title = extract(text, '.*?一审刑事判决书')  # 文书名
            province = extract(text, '(\(2022\))(.{1})(\d+)', 2)  # 省份
            date_time = extract(text, '二〇.*?日')  # 判决日期
            criminal = extract(text, '(被告人)([^因。，.,]{1,7})(犯)', 2)  # 犯罪嫌疑人姓名

            # 拘役或有期徒刑时长
            imprisonment = extract(text, '(判处)(拘役|有期徒刑)([^，。；（）\(,]+)(日|个月|年)')
            try:
                imprisonment = int(penalty_process(imprisonment))
            except:
                imprisonment = None

            # 罚金
            penalty = extract(text, '(罚金人民币)([^；。，]+)(元)', 2)
            try:
                penalty = int(money_process(penalty))
            except:
                penalty = None

            # 所用法律
            laws = extract(text, '《.*?》.*?[^《\n，,。、；等及的之规定]+', 3)

            # 检测的血液酒精含量
            alcohol = extract(text, '(酒精|乙醇)(\D+)([\d\.]+)', 3)
            if alcohol and float(alcohol) < 40:
                alcohol = float(alcohol) * 100
            if alcohol and float(alcohol) > 1000:
                alcohol = float(alcohol) / 100

            # 是否有自首情节
            """此处我们判断是否有自首情节的方法是文本中是否含有‘自首’二字，其实并不完全，所统计的应该偏少"""
            if '自首' in text:
                confession = '有自首情节'
            else:
                confession = '无自首情节'

        # 返回一个字典
        info = {'website': website, 'filename': filename, 'title': title,
                'date_time': date_time, 'province': province, 'criminal': criminal,
                'alcohol': alcohol, 'laws': laws, 'confession': confession,
                'imprisonment': imprisonment, 'penalty': penalty}
        return info

    def output(self):
        """将上一个函数得到的字典写入文件中"""

        info = self.find_variables()
        with open('./files/data.csv', 'a', encoding='utf-8', newline='') as f:
            header_list = []
            for k in info.keys():
                header_list.append(k)
            writer = csv.DictWriter(f, header_list)
            writer.writerow(info)


# 读取文件目录中的所有文书并进行处理
for i in files:
    a = Judgement(i)
