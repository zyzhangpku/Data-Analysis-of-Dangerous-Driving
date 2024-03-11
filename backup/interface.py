# coding: utf-8

"""
本程序包含用户图形界面的代码部分。
"""

import tkinter as tk
from extractor import correlation, alcohol_relations, laws


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
        self.win.geometry('800x400')  # 设置大小
        tk.Label(self.win, text='危险驾驶罪一审刑事判决书中的数据统计与展示').pack()

        # 创建容器，以便形成布局嵌套
        self.frame = tk.Frame(self.win)
        self.frame.place(relx=0.5, rely=0.5, x=-200, y=-100)

        # 按钮
        tk.Button(self.frame, text='展示文书中出现次数前6的法律', command=laws, width=50).grid(row=0, column=0)
        tk.Button(self.frame, text='是否有自首情节和罚金间的关系', command=correlation1, width=50)\
            .grid(row=1, column=0)
        tk.Button(self.frame, text='是否有自首情节和刑期间的关系', command=correlation2, width=50)\
            .grid(row=1, column=1)
        tk.Button(self.frame, text='省份和罚金间的关系', command=correlation3, width=50)\
            .grid(row=2, column=0)
        tk.Button(self.frame, text='省份和刑期间的关系', command=correlation4, width=50)\
            .grid(row=2, column=1)
        tk.Button(self.frame, text='罚金与酒精浓度的关系以及回归直线', command=correlation5, width=50)\
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
    correlation(6, -2)


def correlation7():
    correlation(-1, -2)


# 显示主窗口
win0 = tk.Tk()
app = Application(win0)
win0.mainloop()
