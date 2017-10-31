#!/usr/bin/env python
# -*- coding:utf-8 -*-  
# @Time    : 2017/10/31 14:28
# @Author  : CGX

import os
import re

def func(dir):
    desWrite = open("/Users/cuangengxuan/Desktop/PackageInfo.txt", 'wb')
    for file in os.listdir(dir):
        if ".apk" not in file:
            continue

        sourceFile = os.path.join(dir, file)
        output = os.popen("./aapt dump badging "+sourceFile)
        for line in output.readlines():
            result = re.search("package: name='[^']*'", line)
            if result:
                currentPkg = (result.group().replace("'", '').split('='))[1]
                str = file+"\t"+currentPkg+"\r\n"
                desWrite.write(str.encode('utf-8'))
                print(str)
                break

    desWrite.close()



if __name__ == '__main__':
    func("/Users/cuangengxuan/Desktop/UC游戏")