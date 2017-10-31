#!/usr/bin/env python
# -*- coding:utf-8 -*-  
# @Time    : 2017/6/27 14:13
# @Author  : CGX
# 删除项目中的EmobLog日志输出

import os
import shutil
import time

projectPath = '/Users/cuangengxuan/Documents/workspace1/SDKNgpDex_original/src'
# projectPath = '/eyuroot/ngp/gen/NgpDex/src'
jarCodePath = ''  # '/Users/cuangengxuan/Documents/AutoJar'
projectName = '<name>DexNoLog</name>\n'
desPath     = '/Users/cuangengxuan/Documents/Androidstudio/AutoPack/autojar/src/main/java'
deleteKey1 = 'Emoblog'
deleteKey2 = 'LogUtil'

def func():
    if os.path.exists(desPath):
        shutil.rmtree(desPath) # 删除DexNoLog文件夹
    pathList = [projectPath, jarCodePath]
    for pathName in pathList:
        for root, dirs, files in os.walk(pathName):
            for fileName in files:
                srcFilePath = os.path.join(root, fileName)
                if '.DS_Store' in srcFilePath:
                    continue
                # if '.svn' in srcFilePath:
                #     continue
                # if '/bin/' in srcFilePath:
                #     continue
                # if '/gen/' in srcFilePath:
                #     continue
                # if '/EmobLog.java' in srcFilePath:
                #     continue

                # srcFilePath[9:] 获取从9到最后的元素
                desFilePath = desPath + srcFilePath[len(pathName):]

                # 获取文件所在的文件夹
                dirName = os.path.dirname(desFilePath)
                # 如果文件夹不存在则新建
                if not os.path.exists(dirName):
                    os.makedirs(dirName, 0o777)  # 0o777 权限模式
                if '.java' in srcFilePath:
                    srcRead = open(srcFilePath, 'r')
                    desWrite = open(desFilePath, 'w')
                    while True:
                        line = srcRead.readline()
                        if not line:
                            break
                        if (deleteKey1 in line) or (deleteKey2 in line):
                            continue
                        else:
                            desWrite.write(line)

                    srcRead.close()
                    desWrite.close()
                elif '.project' in desFilePath:
                    srcRead = open(srcFilePath, 'r')
                    desWrite = open(desFilePath, 'w')
                    a = True;
                    while True:
                        line = srcRead.readline()
                        if not line:
                            break
                        if '<name>' in line and a:
                            line = projectName
                            a = False
                        desWrite.write(line)
                    srcRead.close()
                    desWrite.close()
                else:
                    open(desFilePath, "wb").write(open(srcFilePath, "rb").read())

    # os.system("sh /Users/cuangengxuan/PycharmProjects/TestDemo/app/tools/autojar.sh")






if __name__ == '__main__':
    func()



def getCurTime():
    nowTime = time.localtime()
    year = str(nowTime.tm_year)
    month = str(nowTime.tm_mon)
    if len(month) < 2:
        month = '0' + month
    day =  str(nowTime.tm_yday)
    if len(day) < 2:
        day = '0' + day
    return year + '-' + month + '-' + day