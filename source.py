# coding: utf-8

"""
本程序主要包含四部分。分别用于处理文书、提取变量、处理变量、创造用户图形界面。
"""

import csv
import os
import matplotlib.pyplot as plt
from pylab import xticks, np
import re
import tkinter as tk

# 以下两行是为了确保图标能正常显示汉字
if os.name == 'nt':
    plt.rcParams['font.sans-serif'] = ['SimHei']

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


def extract_penalty(file, exp0, jud_val=0):
    """提取刑期"""

    if jud_val == 1:
        pat_str = '缓刑'
        try:
            ret = ''
            for unit in re.findall(exp0, file)[-1]:
                ret += unit
            pat = re.compile(pat_str)
            m = pat.search(ret)
            true_start = m.start()
            return ret[true_start:]
        except IndexError:
            return None
    else:
        try:
            ret = ''
            for unit in re.findall(exp0, file)[-1]:
                ret += unit
            return ret
        except IndexError:
            return None


def find_start(file):
    """寻找判决结果"""

    flag_words = ['裁判结果', '判决结果', '判决主文']
    for wo in flag_words:
        if wo in file:
            start_index = file.find(wo)
            return start_index
    return None


def file_process_for_extraction(file):
    """截取判决结果的一部分，在这部分中寻找判决结果"""

    if find_start(file):
        start_index = find_start(file)
        return file[start_index:]
    else:
        return ' '


def penalty_process(penalty):
    """将用汉语数字表达的刑期转化为数字，单位是天数"""

    if penalty and len(penalty) >= 12:
        return None
    if penalty == '判处拘役一个月二十五日':
        return 55
    penalty = penalty.lstrip('判处').lstrip('拘役').lstrip('缓刑').lstrip('有期徒刑')
    trans0 = ['亿', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', '=', '十一', '十二', '十三', '十四',
              '十五', '十六', '十七', '十八', '十九', '二十', 'q', 'w', 'e', 'r', '二十五']
    trans = ['亿', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    if '至' in penalty:
        return 30
    if '两' in penalty:
        penalty = penalty.replace('两', '二')
    for kanji in trans0:
        if kanji in penalty:
            penalty = penalty.replace(kanji, str(trans0.index(kanji)))
    for kanji in trans:
        if kanji in penalty:
            penalty = penalty.replace(kanji, str(trans.index(kanji)))
    if '十' in penalty:
        penalty = penalty.replace('十', '10')
    if '零' in penalty:
        penalty = penalty.replace('零', '')
    if '个' in penalty:
        penalty = penalty.replace('个', '')
    if '又' in penalty:
        penalty = penalty.replace('又', '')
    if '年' in penalty:
        penalty = penalty.replace('年', '*365+')
    if '月' in penalty:
        penalty = penalty.replace('月', '*30+')
    if '日' in penalty:
        penalty = penalty.replace('日', '*1+')
    penalty += '0'
    try:
        return eval(penalty)
    except SyntaxError:
        return None
    except NameError:
        return None


def money_process(money):
    """将用汉语数字表达的罚金转化为数字，单位是元"""

    tot = 0
    if not money:
        return None
    try:
        money0 = int(money)
        return money0
    except ValueError:
        trans = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四']
        for kj in money:
            if kj.isdigit():
                money = money.replace(str(kj), trans[int(kj)])
        if '万' in money:
            if money[0] == '两':
                money = '二' + money[1:]
            money = money.split('万')
            try:
                tot += trans.index(money[0]) * 10000
            except ValueError:
                return None
            money = money[-1]
        if '千' in money:
            if money[0] == '两':
                money = '二' + money[1:]
            money = money.split('千')
            tot += trans.index(money[0]) * 1000
            money = money[-1]
        if '百' in money:
            if money[0] == '两':
                money = '二' + money[1:]
            tot += trans.index(money[0]) * 100
        if tot == 0:
            return None
        return tot


"""
第二部分的目的是从下载的1299个文书中提取变量。
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

            filename = self.filepath  # 文件名称
            website = extract(_text, 'https:.*?.html')  # 源网站
            _title = extract(_text, '.*?一审刑事判决书')  # 文书名
            province = extract(_text, '(\(2022\))(.{1})(\d+)', 2)  # 省份
            date_time = extract(_text, '二〇.*?日')  # 判决日期
            criminal = extract(_text, '(被告人)([^因。，.,]{1,7})(犯)', 2)  # 犯罪嫌疑人姓名

            # 所用法律
            _laws = extract(_text, '《.*?》.*?[^《\n，,。、；等及的之规定]+', 3)

            # 是否有自首情节
            """此处我们判断是否有自首情节的方法是文本中是否含有‘自首’二字，其实并不完全，所统计的应该偏少"""
            if '自首' in _text:
                confession = '有自首情节'
            else:
                confession = '无自首情节'

            # 检测的血液酒精含量
            alcohol = extract(_text, '(酒精|乙醇)(\D+)([\d\.]+)', 3)
            if alcohol and float(alcohol) < 40:
                alcohol = round(float(alcohol) * 100)
            if alcohol and float(alcohol) > 1000:
                alcohol = round(float(alcohol) / 100)
            if alcohol:
                alcohol = round(float(alcohol))
            if alcohol and float(alcohol) < 80:
                alcohol = None

            # 截取判决结果
            _text_processed = file_process_for_extraction(_text)

            # 拘役或有期徒刑时长
            imprisonment = extract_penalty(_text_processed, '(判处)(拘役|有期徒刑)([^，。；、（）\(,]+)(日|个月|年)')
            try:
                imprisonment = penalty_process(imprisonment)
            except AttributeError:
                imprisonment = None

            # 罚金
            penalty = extract(_text_processed, '(罚金人民币|罚金)([^；。，]+?)(元)', 2)
            try:
                penalty = int(money_process(penalty))
            except AttributeError:
                penalty = None
            except TypeError:
                penalty = None

            # 缓刑
            probation = extract_penalty(_text_processed, '(拘役|有期徒刑)(.*?)(缓刑)([^，。；（）\(,]+)(日|个月|年)', 1)
            try:
                probation = penalty_process(probation)
            except AttributeError:
                probation = None

        # 返回一个字典
        _info = {'website': website, 'filename': filename, 'title': _title,
                 'date_time': date_time, 'province': province, 'criminal': criminal,
                 'alcohol': alcohol, 'probation': probation, 'laws': _laws, 'confession': confession,
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


"""
# 读取文件目录
files = os.listdir('./material/input/')

# 读取文件目录中的所有文书并进行处理
for file_0 in files:
    results = Judgement(file_0)
"""

"""
第三部分包含一系列函数，主要是处理data.csv，并绘图展示其处理结果。
"""


def rg_eq(alist, blist):
    """给定两个用于画图的列表，求出其线性回归方程和相关系数"""

    n = len(alist)
    x_ave = sum(alist) / n
    y_ave = sum(blist) / n

    # 求解过程
    temp1 = temp2 = temp3 = temp4 = temp5 = 0
    for i in range(n):
        temp1 += alist[i] * blist[i]
        temp2 += alist[i] ** 2
        temp3 += (alist[i] - x_ave) * (blist[i] - y_ave)
        temp4 += (alist[i] - x_ave) ** 2
        temp5 += (blist[i] - y_ave) ** 2
    temp1 -= n * x_ave * y_ave
    temp2 -= n * x_ave ** 2
    b = temp1 / temp2
    a = y_ave - x_ave * b
    r = temp3 / (temp4 * temp5) ** 0.5

    return b, a, r


def draw_line(b, a, ax0):
    """画出回归方程"""

    x_values = range(1, 50001)
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


def laws():
    """读取文件并统计出现次数前6的法律，然后直接作图"""
    law = {}

    # 读取文件
    with open('./material/output/data.csv', encoding='utf-8') as f6:
        reader = csv.reader(f6)
        u = [row[8] for row in reader]
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


def alcohol_relations(a1, b):
    """读取文件中的两列数据并绘图，a=6是酒精浓度，a=4是省份，b=-1是罚金，b=-2是刑期"""
    data = []

    # 读取数据
    with open('./material/output/data.csv', encoding='utf-8') as f4:
        for line in f4.readlines():
            line = line.rstrip('\n').split(',')
            if line[a1] != '' and line[b] != '' and line[-3] == '无自首情节' and line[7] == '':
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

    # 作图设置
    if a1 == 6:
        plt.xlabel('酒精浓度，单位：mg/100ml')
        if b == -2:
            plt.ylabel('拘役或有期徒刑天数，单位：天')
            ax.axis([80, 365, 0, 200])
            plt.title(f'（无自首情节、无缓刑）拘役或有期徒刑天数与酒精浓度的关系 （相关系数{r}）')
        elif b == -1:
            plt.ylabel('罚金，单位：元')
            ax.axis([80, 365, 0, 30000])
            plt.title(f'（无自首情节、无缓刑）罚金与酒精浓度的关系 （相关系数{r}）')
    elif a1 == -1 and b == -2:
        plt.xlabel('罚金，单位：元')
        plt.ylabel('拘役或有期徒刑天数，单位：天')
        plt.title(f'（无自首情节、无缓刑）拘役或有期徒刑天数与罚金的关系 （相关系数{r}）')
        ax.axis([0, 30000, 0, 200])
    else:
        pass
    draw_line(b0, a0, ax)
    plt.show()

    return None


def statistic_province(a, b, ave, s):
    """读取文件中的两列数据，a=4是省份，a=-3是是否有自首情节，b=-1是罚金，b=-2是刑期。"""

    # 我们希望分析省份和是否有自首情节这两者是否和罚金与刑期有关，也即罚金和刑期是否具有地域差异和自首情节是否被纳入参考。
    # 因此我们需要控制变量。虽然我们提前知道酒精浓度和罚金与刑期有极弱的线性相关关系，但我们还是控制酒精浓度近似不变。
    # 我们认为两个酒精浓度的数据在[μ-σ,μ+σ]中是无差异的，其中通过上一个函数，我们求出了平均值μ和方差σ。

    l1 = []
    with open('./material/output/data.csv', encoding='utf-8') as f6:
        for line in f6.readlines():
            line = line.rstrip('\n').split(',')
            if b != 7:
                flag = line[a] != '' and line[-6] != '' and line[b] != ''
            else:
                flag = line[a] != '' and line[-6] != ''
            if a == 4:
                flag1 = line[7] == '' and line[-3] == '无自首情节'
            elif a == -3:
                if b != 7:
                    flag1 = line[7] == ''
                else:
                    flag1 = True
            if flag and flag1:
                try:
                    x = int(line[a])
                except ValueError:
                    x = line[a]
                try:
                    y = float(line[-6])
                except ValueError:
                    y = -1
                if b != 7:
                    try:
                        z = float(line[b])
                    except ValueError:
                        z = line[b]
                else:
                    if line[7] == '':
                        z = 0
                    else:
                        z = 100
                if b != 6:
                    if ave - 2 * s <= y <= ave + 2 * s:
                        l1.append((x, z))
                else:
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
    if a == 4:
        if b == -1:
            plt.ylim(0, 25000)
            plt.ylabel('罚金，单位：元')
            plt.xlabel('省份（仅取样本较多的省份展示）')
            plt.title('（无自首、无缓刑）省份和罚金间的关系')
        elif b == -2:
            plt.ylabel('刑期，单位：天')
            plt.xlabel('省份（仅取样本较多的省份展示）')
            plt.ylim(0, 100)
            plt.title('（无自首、无缓刑）省份和刑期间的关系')
        elif b == 6:
            plt.ylabel('酒精浓度，单位：mg/100ml')
            plt.xlabel('省份（仅取样本较多的省份展示）')
            plt.ylim(0, 265)
            plt.title('（无自首、无缓刑）省份和酒精浓度间的关系')
    elif a == -3:
        if b == -2:
            plt.ylim(0, 80)
            plt.ylabel('刑期，单位：天')
            plt.title('（无缓刑情况）是否有自首情节和刑期间的关系')
        elif b == -1:
            plt.ylim(0, 6000)
            plt.ylabel('罚金，单位：元')
            plt.title('（无缓刑情况）是否有自首情节和罚金间的关系')
        elif b == 7:
            plt.ylim(0, 100)
            plt.ylabel('有缓刑的占比，单位：%')
            plt.title('是否有自首情节和是否有缓刑间的关系')

    plt.show()


def draw_barchart(val):
    """进行单变量的统计并作出柱状图，val=-1是罚金，val=-2是刑期,val=6是酒精浓度，val=7是缓刑"""

    # 读取文件
    val_bar = []
    if val == -1:
        a, b, c, best_n = 1, 31, 16, 1000
        x_title, y_title, all_tile = '罚金，单位：千元', '数量', '罚金统计图（最大值33，最小值1，平均值4656）'
    elif val == -2:
        a, b, c, best_n = 1, 8, 8, 30
        x_title, y_title, all_tile = '刑期（拘役或有期徒刑），单位：月', '数量', \
                                     '刑期（拘役或有期徒刑）统计图（最大值8，最小值1，平均值1.9）'
    elif val == 6:
        a, b, c, best_n = 80, 365, 8, 1
        x_title, y_title, all_tile = '酒精浓度，单位：mg/100ml', '数量', \
                                     '酒精浓度统计图（最大值365，最小值80，平均值164.5）'
    else:
        a, b, c, best_n = 1, 20, 20, 30
        x_title, y_title, all_tile = '缓刑，单位：月', '数量', \
                                     '缓刑统计图（最大值18，最小值30，平均值3.0）（有缓刑者占比38.5%）'
    with open('./material/output/data.csv', encoding='utf-8') as f_bar:
        for line in f_bar.readlines():
            line = line.rstrip('\n').split(',')
            if line[val] != '':
                val_bar.append(int(line[val]) / best_n)

    # 绘图
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(all_tile)
    xticks(np.linspace(a, b, c, endpoint=True))
    plt.hist(val_bar, bins=c)
    plt.show()


"""
# 以下函数用于测试
draw_barchart(-1)
draw_barchart(-2)
draw_barchart(6)
draw_barchart(7)
laws()
correlation(-3, -1)
correlation(-3, -2)
correlation(-3, 7)
correlation(4, -1)
correlation(4, -2)
correlation(4, 6)
alcohol_relations(6, -1)
alcohol_relations(6, -2)
alcohol_relations(-1, -2)
"""

"""
第四部分包含图形用户界面部分。
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
        self.win.geometry('1000x600')  # 设置大小
        tk.Label(self.win, text='危险驾驶罪一审刑事判决书中的数据统计与展示').pack()

        # 创建容器，以便形成布局嵌套
        self.frame = tk.Frame(self.win)
        self.frame.place(relx=0.5, rely=0.5, x=-400, y=-150)

        # 按钮
        tk.Button(self.frame, text='文书中出现次数前6的法律', command=laws, width=55).grid(row=0, column=0)

        tk.Button(self.frame, text='罚金统计', command=show1, width=55).grid(row=2, column=0)
        tk.Button(self.frame, text='拘役或有期徒刑天数统计', command=show2, width=55).grid(row=2, column=1)
        tk.Button(self.frame, text='酒精浓度统计', command=show3, width=55).grid(row=3, column=0)
        tk.Button(self.frame, text='缓刑天数统计', command=show4, width=55).grid(row=3, column=1)

        tk.Button(self.frame, text='是否有自首情节和罚金间的关系（酒精浓度接近、无缓刑情况）',
                  command=correlation1, width=55).grid(row=5, column=0)
        tk.Button(self.frame, text='是否有自首情节和刑期间的关系（酒精浓度接近、无缓刑情况）',
                  command=correlation2, width=55).grid(row=5, column=1)
        tk.Button(self.frame, text='是否有自首情节和是否有缓刑间的关系（酒精浓度接近）',
                  command=add1, width=55).grid(row=6, column=0)

        tk.Button(self.frame, text='省份和罚金间的关系（酒精浓度接近、无缓刑和自首情况）',
                  command=correlation3, width=55).grid(row=7, column=0)
        tk.Button(self.frame, text='省份和刑期间的关系（酒精浓度接近、无缓刑和自首情况）',
                  command=correlation4, width=55).grid(row=7, column=1)
        tk.Button(self.frame, text='省份和酒精浓度间的关系（无缓刑和自首情况）',
                  command=add2, width=55).grid(row=8, column=0)

        tk.Button(self.frame, text='罚金与酒精浓度的关系以及回归直线（无缓刑和自首情况）',
                  command=correlation5, width=55).grid(row=9, column=0)
        tk.Button(self.frame, text='拘役或有期徒刑天数与酒精浓度的关系以及回归直线（无缓刑和自首情况）',
                  command=correlation6, width=55).grid(row=9, column=1)
        tk.Button(self.frame, text='拘役或有期徒刑天数与罚金的关系以及回归直线（无缓刑和自首情况）',
                  command=correlation7, width=55).grid(row=10, column=0)


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


def show1():
    draw_barchart(-1)


def show2():
    draw_barchart(-2)


def show3():
    draw_barchart(6)


def show4():
    draw_barchart(7)


def add1():
    correlation(-3, 7)


def add2():
    correlation(4, 6)


# 显示主窗口
win0 = tk.Tk()
app = Application(win0)
win0.mainloop()
