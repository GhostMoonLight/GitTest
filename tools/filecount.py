#!/usr/bin/env python
# -*- coding:utf-8 -*-  
# @Time    : 2017/10/18 13:51
# @Author  : CGX


import tkinter

import sys,os
def fileCountIn(dir):

    list = os.listdir(dir)

    while True:
        if '.DS_Store' in list:
            list.remove('.DS_Store')
        else:
            break

    print(list)

    return len(list)


if __name__ == '__main__':
    fileCountIn("/Users/cuangengxuan/Desktop/proguard/AutoInsert/sopath")
    top = tkinter.Tk()
    # 进入消息循环
    top.mainloop()