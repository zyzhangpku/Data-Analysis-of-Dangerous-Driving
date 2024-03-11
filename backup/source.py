# coding: utf-8

"""
本程序主要包含四部分。分别用于处理文书、提取变量、处理变量、创造用户图形界面。
"""

import csv
import os
import matplotlib.pyplot as plt
import re
import tkinter as tk

if os.name == 'nt':
    plt.rcParams['font.sans-serif'] = ['SimHei']
# 以下两行是为了确保图标能正常显示汉字


# 读取文件目录
files = os.listdir('./material/input/')

"""
第一部分包含三个函数，主要在处理文书时用到。
"""


def extract(file, exp0, num=0):
    """提取单个变量"""
    try:
        target = re.search(exp0, file).group(num)
        return target
    except IndexError:
        return re.findall(exp0, file)
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
        return 365 * 10 + 6 * 30
    if penalty == '1个月':
        return 30
    if penalty == '10个月':
        return 300
    if penalty == '11个月':
        return 11 * 30
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
    except TypeError:
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


"""
第二个的目的是从下载的1299个文书中提取变量。
为方便后续的处理，提取的变量将被储存至material/output文件中的data.csv中。
后续的数据处理工作将直接读取data.csv。
"""


class Judgement:
    """表示判决文书的类"""

    def __init__(self, filepath):
        self.filepath = './material/input/' + filepath
        if self.judge():
            self.output()

    def judge(self):
        """判断该文件是否为一审刑事判决书"""

        with open(self.filepath, encoding='utf-8') as f1:
            f1.readline()
            f1.readline()
            if '一审刑事判决书' in f1.readline():
                return True
            else:
                return False

    def find_variables(self):
        """从文书中提取变量"""

        with open(self.filepath, encoding='utf-8') as f2:
            _text = f2.read()

            filename = self.filepath[8:]  # 文件名称
            website = extract(_text, 'https:.*?.html')  # 源网站
            _title = extract(_text, '.*?一审刑事判决书')  # 文书名
            province = extract(_text, '(\(2022\))(.{1})(\d+)', 2)  # 省份
            date_time = extract(_text, '二〇.*?日')  # 判决日期
            criminal = extract(_text, '(被告人)([^因。，.,]{1,7})(犯)', 2)  # 犯罪嫌疑人姓名

            # 拘役或有期徒刑时长
            imprisonment = extract(_text, '(判处)(拘役|有期徒刑)([^，。；（）\(,]+)(日|个月|年)')
            try:
                imprisonment = int(penalty_process(imprisonment))
            except:
                imprisonment = None

            # 罚金
            penalty = extract(_text, '(罚金人民币)([^；。，]+)(元)', 2)
            try:
                penalty = int(money_process(penalty))
            except:
                penalty = None

            # 所用法律
            _laws = extract(_text, '《.*?》.*?[^《\n，,。、；等及的之规定]+', 3)

            # 检测的血液酒精含量
            alcohol = extract(_text, '(酒精|乙醇)(\D+)([\d\.]+)', 3)
            if alcohol and float(alcohol) < 40:
                alcohol = float(alcohol) * 100
            if alcohol and float(alcohol) > 1000:
                alcohol = float(alcohol) / 100

            # 是否有自首情节
            """此处我们判断是否有自首情节的方法是文本中是否含有‘自首’二字，其实并不完全，所统计的应该偏少"""
            if '自首' in _text:
                confession = '有自首情节'
            else:
                confession = '无自首情节'

        # 返回一个字典
        _info = {'website': website, 'filename': filename, 'title': _title,
                 'date_time': date_time, 'province': province, 'criminal': criminal,
                 'alcohol': alcohol, 'laws': _laws, 'confession': confession,
                 'imprisonment': imprisonment, 'penalty': penalty}
        return _info

    def output(self):
        """将上一个函数得到的字典写入文件中"""

        info_ = self.find_variables()
        with open('./material/output/data.csv', 'a', encoding='utf-8', newline='') as f3:
            header_list = []
            for k in info_.keys():
                header_list.append(k)
            writer = csv.DictWriter(f3, header_list)
            writer.writerow(info_)


# 读取文件目录中的所有文书并进行处理
for file_0 in files:
    results = Judgement(file_0)

"""
第三部分包含一系列函数，主要是处理data.csv，并绘图展示其处理结果。
"""


def alcohol_relations(a1, b):
    """读取文件中的两列数据并绘图，a=6是酒精浓度，a=4是省份，b=-1是罚金，b=-2是刑期"""
    data = []

    # 读取数据
    with open('./material/output/data.csv', encoding='utf-8') as f4:
        for line in f4.readlines():
            line = line.rstrip('\n').split(',')
            if line[a1] != '' and line[b] != '':
                try:
                    x = float(line[a1])
                except ValueError:
                    x = line[a1]
                try:
                    y = float(line[b])
                except ValueError:
                    y = line[b]

                data.append((x, y))
    data = sorted(data, key=lambda _i: _i[1])
    alist, blist = zip(*data)

    # 准备画图
    fig, ax = plt.subplots()
    ax.scatter(alist, blist)
    b0, a0, r = rg_eq(alist, blist)

    if a1 == 6:
        plt.xlabel('酒精浓度，单位：mg/100ml')
        if b == -2:
            plt.ylabel('拘役或有期徒刑天数，单位：天')
            ax.axis([80, 300, 0, 200])
            plt.title(f'拘役或有期徒刑天数与酒精浓度的关系 （相关系数{r}）')
        elif b == -1:
            plt.ylabel('罚金，单位：元')
            ax.axis([80, 300, 0, 20000])
            plt.title(f'罚金与酒精浓度的关系 （相关系数{r}）')
    elif a1 == -1 and b == -2:
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
    with open('./material/output/data.csv', encoding='utf-8') as f5:
        for line in f5.readlines():
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
    with open('./material/output/data.csv', encoding='utf-8') as f6:
        for line in f6.readlines():
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

    _average, sigma = statistic_province_average_and_sigma()
    l0 = statistic_province(a, b, _average, sigma)
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
    with open('./material/output/data.csv', encoding='utf-8') as f6:
        reader = csv.reader(f6)
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

"""
第四部分包含用户图形界面部分。
这一部分参考了本节课的参考用书《Python程序设计》最后一章。
"""


class Application:

    def __init__(self, win=None):
        self.label = None
        self.button = None
        self.entry = None
        self.degreeC = None
        self.frame = None
        self.win = win
        self.init_widgets()

    def init_widgets(self):
        """初始化界面、创建子组件"""

        # 窗口
        self.win.title('危险驾驶罪一审刑事判决书中的数据统计与展示')  # 设置窗口标题
        self.win.geometry('1000x400')  # 设置大小
        tk.Label(self.win, text='危险驾驶罪一审刑事判决书中的数据统计与展示').pack()

        # 创建容器，以便形成布局嵌套
        self.frame = tk.Frame(self.win)
        self.frame.place(relx=0.5, rely=0.5, x=-200, y=-100)

        # 按钮
        tk.Button(self.frame, text='展示文书中出现次数前6的法律', command=laws, width=50).grid(row=0, column=0)
        tk.Button(self.frame, text='是否有自首情节和罚金间的关系', command=correlation1, width=50) \
            .grid(row=1, column=0)
        tk.Button(self.frame, text='是否有自首情节和刑期间的关系', command=correlation2, width=50) \
            .grid(row=1, column=1)
        tk.Button(self.frame, text='省份和罚金间的关系', command=correlation3, width=50) \
            .grid(row=2, column=0)
        tk.Button(self.frame, text='省份和刑期间的关系', command=correlation4, width=50) \
            .grid(row=2, column=1)
        tk.Button(self.frame, text='罚金与酒精浓度的关系以及回归直线', command=correlation5, width=50) \
            .grid(row=3, column=0)
        tk.Button(self.frame, text='拘役或有期徒刑天数与酒精浓度的关系以及回归直线', command=correlation6,
                  width=50).grid(row=3, column=1)
        tk.Button(self.frame, text='拘役或有期徒刑天数与罚金的关系以及回归直线', command=correlation7,
                  width=50).grid(row=4, column=0)


def correlation1():
    correlation(-3, -1)


def correlation2():
    correlation(-3, -2)


def correlation3():
    correlation(4, -1)


def correlation4():
    correlation(4, -2)


def correlation5():
    alcohol_relations(6, -1)


def correlation6():
    alcohol_relations(6, -2)


def correlation7():
    alcohol_relations(-1, -2)


# 显示主窗口
win0 = tk.Tk()
app = Application(win0)
win0.mainloop()
