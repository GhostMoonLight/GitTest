#!/usr/bin/env python
# -*- coding:utf-8 -*-  
# @Time    : 2017/6/7 11:36
# @Author  : CGX
# 提供外壳shell.apk和源src.apk，自动把src代码添加到shell.apk中

import zipfile
import os
import hashlib
import zlib
import shutil

srcDir = '/Users/cuangengxuan/Desktop/proguard/AutoPack/'
unzipDir = srcDir + 'pack'  # 解压目录
newZipName = srcDir + 'new.zip'  # 加壳后的apk
disApk = srcDir + 'shell.apk'  # 外壳apk
srcApk = srcDir + 'src.apk'  # 需要加壳的apk
disDex = srcDir + 'disDex.dex'  # 外壳apk的dex
newDex = unzipDir + '/classes.dex'  # 新生成的dex
channelFile = '802'
channel = 'D'+channelFile
signCmd = 'jarsigner -verbose -keystore /Users/cuangengxuan/Desktop/apk/'+channelFile+'.keystore ' \
          '-storepass emob123 -keypass emob123 -sigfile CERT -digestalg SHA1 -sigalg ' \
          'MD5withRSA -signedjar ' + srcDir + 'Apk_521_'+channel+'.apk ' + srcDir + 'new.zip '+channel

# 打包
def autoPack():
    # 解压
    unzip_file(disApk, unzipDir)

    # 替换dex
    payloadArray = encrpt(getBytesFromFile(srcApk))  # 源apk转换成字节，并进行加密
    payloadLen = len(payloadArray)  # 获取字节数组的长度
    unShellDexArray = getBytesFromFile(disDex)  # 外壳的dex转换成字节数组
    unShellDexLen = len(unShellDexArray)
    totalLen = payloadLen + unShellDexLen + 4  # 多出4字节是存放长度的。

    # 创建一个长度为totalLen的字节数组
    newDexBytes = bytearray(totalLen)
    # 把外壳dex的字节数组中的数据copy到newDexBytes中
    for index in range(0, unShellDexLen):
        newDexBytes[index] = unShellDexArray[index]

    # 把源apk的字节数据copy到newDexBytes中
    for index in range(unShellDexLen, unShellDexLen + payloadLen):
        newDexBytes[index] = payloadArray[index - unShellDexLen]

    # 把源apk的长度字节数组数据放到newDexBytes后四位中
    lenBytes = int2Bytes(payloadLen)
    for index in range(0, 4):
        newDexBytes[unShellDexLen + payloadLen + index] = lenBytes[index]

    fixFileSizeHeader(newDexBytes) # 修改DEX file size文件头
    fixSHA1Header(newDexBytes)     # 修改dex头 sha1值
    fixCheckSumHeader(newDexBytes) # 修改dex头，CheckSum 校验码

    f = open(newDex, 'wb')
    f.write(newDexBytes)
    f.close()

    zip_dir(unzipDir, newZipName)
    os.remove(disDex)  # 删除disDex.dex
    os.system(signCmd)  # 签名
    # 删除解压目录和该目录下的文件
    deleteDirs(unzipDir)
    # os.removedirs(unzipDir)  # 删除解压目录
    os.remove(newZipName)  # 删除new.zip文件


# 解压
def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir):
        os.mkdir(unziptodir, 0o777)

    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        # 解压的时候忽略该目录下的文件
        if 'META-INF' in name:
            continue
        # 获取文件的绝对路径
        ext_filename = os.path.join(unziptodir, name)
        # 获取文件所在的文件夹
        ext_dir = os.path.dirname(ext_filename)
        # 如果文件夹不存在则新建
        if not os.path.exists(ext_dir):
            os.makedirs(ext_dir, 0o777)
        outfile = open(ext_filename, 'wb')
        outfile.write(zfobj.read(name))
        outfile.close()

        # 把classes.dex文件复制到跟目录下，后面需要操作这个文件
        if 'classes.dex' in name:
            outfile = open(os.path.join(srcDir, disDex), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


# 压缩
def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        # print arcname
        zf.write(tar, arcname)

    zf.close()


# 读取文件到字节数组
def getBytesFromFile(filename):
    return open(filename, "rb").read()


# 加密
# 使用内置函数bytearray()来完成从bytes对象到可变的bytearray对象的转换。
# 所有对bytes对象的操作也可以用在bytearray对象上。
# 有一点不同的就是，我们可以使用下标标记给bytearray对象的某个字节赋值。并且，这个值必须是0–255之间的一个整数。
def encrpt(byteArray):
    byteArray = bytearray(byteArray)  # 不经过这一操作，直接byteArray[0] = 221   会报错
    length = len(byteArray)
    for index in range(0, length):
        byteArray[index] = 5 ^ byteArray[index]

    return byteArray


# int转bytes
def int2Bytes(number):
    b = bytearray(4)
    for i in range(0, 4):
        b[3 - i] = number % 256
        number >>= 8
    return b


# 修改DEX file size文件头
def fixFileSizeHeader(bs):
    newLenBytes = int2Bytes(len(bs))
    b = bytearray(4)
    for i in range(0, 4):
        b[i] = newLenBytes[len(newLenBytes) - i - 1]

    for i in range(0, 4):
        bs[32 + i] = b[i]


# 修改dex头 sha1值
def fixSHA1Header(bs):
    md = hashlib.sha1()
    sha1Bytes = bytearray(len(bs) - 32)
    for i in range(32, len(bs)):
        sha1Bytes[i - 32] = bs[i]
    md.update(sha1Bytes)
    newdt = md.digest();
    newdtlen = len(newdt)
    for i in range(0, newdtlen):
        bs[12 + i] = newdt[i]


# 修改dex头，CheckSum 校验码
def fixCheckSumHeader(bs):
    length = len(bs)
    checkSunBytes = bytearray(length - 12)
    for i in range(12, length):
        checkSunBytes[i - 12] = bs[i]

    checksum = zlib.adler32(checkSunBytes)
    newcs = int2Bytes(checksum);
    recs = bytearray(4)
    for i in range(0, 4):
        recs[i] = newcs[len(newcs) - 1 - i];

    for i in range(8, 12):
        bs[i] = recs[i - 8]


# 删除文件夹和文件夹中的所有文件
def deleteDirs(dir):
    shutil.rmtree(dir, True)
    # current_filelist = os.listdir(dir)
    # for f in current_filelist:
    #     filepath = os.path.join(dir, f)
    #     if os.path.isfile(filepath):
    #         os.remove(filepath)
    #     elif os.path.isdir(filepath):
    #         shutil.rmtree(filepath, True)
    # os.removedirs(dir)


if __name__ == '__main__':
    autoPack()
