# coding: utf-8

"""
本程序包含一系列函数，主要在处理文书时用到。
为了保证主程序的简洁性，因此将这些函数写入了该程序而不是直接写入主程序。
"""

import re


def extract(file, exp, num=0):
    """提取单个变量"""
    try:
        target = re.search(exp, file).group(num)
        return target
    except IndexError:
        return re.findall(exp, file)
    except AttributeError:
        return None


def penalty_process(penalty: str):
    """将用汉语数字表达的刑期转化为数字，单位是天数"""
    penalty_days = 0
    penalty = penalty.lstrip('判处')
    if '拘役' in penalty:
        penalty = penalty.lstrip('拘役')
    else:
        penalty = penalty.lstrip('有期徒刑')
    if penalty == '3年':
        return 365 * 3
    if penalty == '10年6个月':
        return 365*10+6*30
    if penalty == '1个月':
        return 30
    if penalty == '10个月':
        return 300
    if penalty == '11个月':
        return 11*30
    if penalty == '2个月':
        return 60
    if penalty == '4个月':
        return 120
    trans = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四']
    if '年' in penalty:
        penalty = penalty.split('年')
        penalty_days += trans.index(penalty[0]) * 365
        penalty = penalty[-1]
    try:
        if penalty[0] == '零':
            penalty = penalty.lstrip('零')
    except IndexError:
        pass
    if '个月' in penalty:
        if penalty[0] == '两':
            penalty = '二' + penalty[1:]
        penalty = penalty.split('个月')
        penalty_days += trans.index(penalty[0]) * 30
        penalty = penalty[-1]
    if '日' in penalty:
        if '又' in penalty:
            penalty = penalty.lstrip('又')
        if len(penalty) <= 2:
            penalty = penalty.split('日')
            penalty_days += trans.index(penalty[0])
        elif penalty[1] != '十':
            penalty_days += trans.index(penalty[0]) * 10 + trans.index(penalty[1])
        else:
            penalty_days += trans.index(penalty[0]) * 10
    return penalty_days


def money_process(money):
    """将用汉语数字表达的罚金转化为数字，单位是元"""
    tot = 0
    try:
        money = int(money)
        return money
    except:
        trans = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四']

        if '万' in money:
            money = money.split('万')
            tot += trans.index(money[0]) * 10000
            money = money[-1]
        if '千' in money:
            money = money.split('千')
            tot += trans.index(money[0]) * 1000
            money = money[-1]
        if '百' in money:
            tot += trans.index(money[0]) * 100
        if tot == 0:
            return None
        return tot
