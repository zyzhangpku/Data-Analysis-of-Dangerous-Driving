# coding: utf-8

"""
本程序包含一系列函数，主要是处理data.csv，并展示其处理结果。
"""

from pylab import *
import matplotlib.pyplot as plt
import csv

# 以下两行是为了确保图标能正常显示汉字
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


def alcohol_relations(a, b):
    """读取文件中的两列数据并绘图，a=6是酒精浓度，a=4是省份，b=-1是罚金，b=-2是刑期"""
    data = []

    # 读取数据
    with open('./files/data.csv', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.rstrip('\n').split(',')
            if line[a] != '' and line[b] != '':
                try:
                    x = float(line[a])
                except ValueError:
                    x = line[a]
                try:
                    y = float(line[b])
                except ValueError:
                    y = line[b]

                data.append((x, y))
    data = sorted(data, key=lambda i: i[1])
    alist, blist = zip(*data)

    # 准备画图
    fig, ax = plt.subplots()
    ax.scatter(alist, blist)
    b0, a0, r = rg_eq(alist, blist)

    if a == 6:
        plt.xlabel('酒精浓度，单位：mg/100ml')
        if b == -2:
            plt.ylabel('拘役或有期徒刑天数，单位：天')
            ax.axis([80, 300, 0, 200])
            plt.title(f'拘役或有期徒刑天数与酒精浓度的关系 （相关系数{r}）')
        elif b == -1:
            plt.ylabel('罚金，单位：元')
            ax.axis([80, 300, 0, 20000])
            plt.title(f'罚金与酒精浓度的关系 （相关系数{r}）')
    elif a == -1 and b == -2:
        plt.xlabel('罚金，单位：元')
        plt.ylabel('拘役或有期徒刑天数，单位：天')
        plt.title(f'拘役或有期徒刑天数与罚金的关系 （相关系数{r}）')
        ax.axis([0, 20000, 0, 500])
    else:
        pass
    draw_line(b0, a0, ax)
    plt.show()

    return None


def rg_eq(alist, blist):
    """给定两个用于画图的列表，求出其线性回归方程和相关系数"""

    n = len(alist)
    x_ave = sum(alist) / n
    y_ave = sum(blist) / n

    # 剔除过于离谱的数据。标准是比平均值大十倍以上。
    # 这些数据出现的原因主要是有些嫌疑人多罪并犯，导致其刑期或罚金远远超出了其他人。
    # 但是这一剔除并不成功，会导致线性回归方程比较离谱。因此我将这一过程删掉了，但代码保留。
    """
    for i in range(n):
        if alist[i] / x_ave > 10 or blist[i] / y_ave > 10:
            x_ave = (x_ave*n-alist[i])/(n-1)
            y_ave = (y_ave*n-blist[i])/(n-1)
    """

    # 求解过程
    temp1 = temp2 = temp3 = temp4 = temp5 = 0
    for i in range(n):
        """
        if alist[i] / x_ave > 10 or blist[i] / y_ave > 10:
            continue
        """
        temp1 += alist[i] * blist[i]
        temp2 += alist[i] ** 2
        temp3 += (alist[i] - x_ave) * (blist[i] - y_ave)
        temp4 += (alist[i] - x_ave) ** 2
        temp5 += (blist[i] - y_ave) ** 2
    temp1 -= n * x_ave * y_ave
    temp2 -= n * x_ave ** 2
    b = temp1 / temp2
    a = x_ave * b + y_ave
    r = temp3 / (temp4 * temp5) ** 0.5

    return b, a, r


def draw_line(b, a, ax0):
    """画出回归方程"""

    x_values = range(1, 20001)
    y_values = [b * x + a for x in x_values]
    ax0.scatter(x_values, y_values)
    return None


def statistic_province_average_and_sigma():
    """读取文件的的酒精浓度的数据，求出其平均值和方差"""

    data = []
    with open('./files/data.csv', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.rstrip('\n').split(',')
            if line[-6] != '':
                try:
                    x = float(line[-6])
                    data.append(x)
                except ValueError:
                    pass
    ave = sum(data) / len(data)
    s = 0
    for i in data:
        s += (i - ave) ** 2

    return ave, (s / len(data)) ** 0.5


def statistic_province(a, b, ave, s):
    """读取文件中的两列数据，a=4是省份，a=-3是是否有自首情节，b=-1是罚金，b=-2是刑期。"""

    # 我们希望分析省份和是否有自首情节这两者是否和罚金与刑期有关，也即罚金和刑期是否具有地域差异和自首情节是否被纳入参考。
    # 因此我们需要控制变量。虽然我们提前知道酒精浓度和罚金与刑期有极弱的线性相关关系，但我们还是控制酒精浓度近似不变。
    # 我们认为两个酒精浓度的数据在[μ-σ,μ+σ]中是无差异的，其中通过上一个函数，我们求出了平均值μ和方差σ。

    l1 = []
    with open('./files/data.csv', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.rstrip('\n').split(',')
            if line[a] != '' and line[-6] != '' and line[b] != '':
                try:
                    x = int(line[a])
                except ValueError:
                    x = line[a]
                try:
                    y = float(line[-6])
                except ValueError:
                    y = -1
                try:
                    z = float(line[b])
                except ValueError:
                    z = line[b]
                if ave - s <= y <= ave + s:
                    l1.append((x, z))

    """本函数返回一个列表，储存自变量（省份、是否有自首情节）和因变量（罚金、刑期）。"""
    return l1


def correlation(a, b):
    """根据上一个函数返回的列表作图"""

    average, sigma = statistic_province_average_and_sigma()
    l0 = statistic_province(a, b, average, sigma)
    d0 = {}

    # 计数
    for i in l0:
        if i[0] in d0.keys():
            d0[i[0]][0] += 1
            d0[i[0]][1] += i[-1]
        else:
            d0[i[0]] = [1, 0]
            d0[i[0]][1] += i[-1]

    # 算平均值
    d1 = {}
    for k, v in d0.items():
        d1[k] = v[-1] / v[0]

    # 作图
    alist = []
    blist = []
    for k, v in d1.items():
        alist.append(k)
        blist.append(d1[k])
    fig, ax = plt.subplots()
    ax.bar(alist, blist)

    # 作图设置
    if b == -1 and a == 4:
        plt.ylim(0, 6000)
        plt.ylabel('罚金，单位：元')
        plt.xlabel('省份（仅取样本较多的省份展示）')
        plt.title('省份和罚金间的关系')
    elif b == -2 and a == 4:
        plt.ylabel('刑期，单位：天')
        plt.xlabel('省份（仅取样本较多的省份展示）')
        plt.ylim(0, 500)
        plt.title('省份和刑期间的关系')
    if a == -3:
        if b == -2:
            plt.ylim(100, 150)
            plt.ylabel('刑期，单位：天')
            plt.title('是否有自首情节和刑期间的关系')
        if b == -1:
            plt.ylim(4300, 5200)
            plt.ylabel('罚金，单位：元')
            plt.title('是否有自首情节和罚金间的关系')

    plt.show()


def laws():
    """读取文件并统计出现次数前6的法律，然后直接作图"""
    law = {}

    # 读取文件
    # 这里使用csv包的原因是法律的一列中是一个列表，但是被以字符串的形式写入。如果正常读取很麻烦。
    with open('./files/data.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        u = [row[7] for row in reader]
        for i in u:
            i = i.lstrip("['").rstrip("]'").split("', '")
            # 计数
            for k in i:
                if k in law.keys():
                    law[k] += 1
                else:
                    law[k] = 1

    law_list = []
    law_list_cnt = []
    for la, cnt in law.items():
        law_list.append([la, cnt])

    # 对个数进行排序，并选择前6为展示
    law_list = sorted(law_list, key=lambda x: x[-1], reverse=True)
    final_law_list = []
    for _ in range(6):
        law_list_cnt.append(law_list[_][-1])
        final_law_list.append(law_list[_][0])

    # 绘图
    plt.pie(law_list_cnt, labels=final_law_list, autopct='%0.2f%%')
    plt.axis('equal')
    plt.title('文书中出现次数前6的法律')
    plt.show()


"""
以下均为测试用
laws()
correlation(-3, -1)
correlation(-3, -2)
correlation(4, -1)
correlation(4, -2)
alcohol_relations(6, -1)
alcohol_relations(6, -2)
alcohol_relations(-1, -2)
"""
