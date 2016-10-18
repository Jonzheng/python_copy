#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    文件预处理脚本
        多线程
        远程ftp获取文件
        文件分发、备份等
"""

import ConfigParser

import string, os, sys, shutil

import paramiko

import re

import time,datetime

#初始化，读取配置

def getCfg(cfgfile = 'prefile.cfg'):
    cfg_dict = {}
    dir_dict = {}
    cf = ConfigParser.ConfigParser()
    cf.read(cfgfile)
    for kv in cf.items(sys.argv[1]):
        cfg_dict[kv[0]] = kv[1]
    #print"label:",sys.argv[1]
    loginfo("label:",sys.argv[1])
    if 'file_prefix' in cfg_dict:
        tmp = cfg_dict['file_prefix']
        tmps = tmp.split(',')
        #print tmp
        for kv in tmps:
            kvs = kv.split(':')
            dir_dict[kvs[0]] = kvs[1]
    return cfg_dict,dir_dict
    
#更新配置
def updateLast(lastFile):
    cf = ConfigParser.ConfigParser()
    cf.read('prefile.cfg')
    cf.set(sys.argv[1], "last_file", lastFile)
    cf.write(open('prefile.cfg',"w"))

#动态输出日志，当日志文件增大时可能会增加开销
def loginfo(*info):
    logfile = sys.argv[1]+".log"
    output = open(logfile, 'a')
    try:
        msg = reduce(lambda x,y:str(x)+str(y),info)
        currtime = "["+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"]  "
        output.write(currtime+msg+"\n")
    except(IOError):
        output.close()
    finally:
        output.close()

#获取远端主机文件
#如果不删除远端文件，那么需要排序记录文件时间
def getRemoteFile(cfg_dict,dirDic):
    orginDir = cfg_dict['origin_dir']
    tmpDir = cfg_dict['temp_dir']
    removeOriginFile = cfg_dict['remove_origin_file']
    lastFile = cfg_dict['last_file']
    try:
        t = paramiko.Transport((cfg_dict['ip_addr'], int(cfg_dict['port'])))
        t.connect(username = cfg_dict['username'] , password = cfg_dict['password'])
        sftp = paramiko.SFTPClient.from_transport(t)
        
       #取所有文件过来
        while 1:
            time.sleep(int(cfg_dict['wait_time']))
            origin_file_list = sftp.listdir(orginDir)
            if len(origin_file_list) > 0:
                for fname in origin_file_list:
                    if fname.endswith('tmp'):
                        continue
                    if removeOriginFile=='False' and fname <= lastFile:
                        continue
                    #拷贝带前缀文件
                    for pre in dirDic:
                        if fname.startswith(pre):
                            origin_file = os.path.join(orginDir,fname)
                            temp_file = os.path.join(tmpDir,fname)
                            sftp.get(origin_file, temp_file)
                            loginfo("getRemoteFile:",fname,",to",tmpDir)
                            sendFile(cfg_dict,dirDic,fname)
                            lastFile = fname
                if removeOriginFile=='True':
                    sftp.remove(origin_file)
    except Exception,ex:
        #print Exception,":",ex
        updateLast(lastFile)
        t.close()
        #exit(-1)
    finally:
        updateLast(lastFile)
        loginfo("-",lastFile)
        t.close()


#发送文件，备份，筛选
def sendFile(cfg_dict,dirDic,filename):
    tmpDir = cfg_dict['temp_dir']
    #destDir = cfg_dict['dest_dir']
    tmpFile = os.path.join(tmpDir,filename)
    #是否整点备份，如果是则在50分之后停止拷贝
    if cfg_dict.get('is_bak_time')=='True':
        minute=datetime.datetime.now().strftime('%M')
        while minute >= '50':
            loginfo("minute >= 50,waiting for backup")
            time.sleep(int(cfg_dict['wait_time']))
            minute=datetime.datetime.now().strftime('%M')
            
    if os.path.isdir(tmpFile):
        return
        
    #不同前缀放入不同目标文件夹
    isInDirDic = False
    for pre in dirDic:
        destDir = dirDic[pre]
        destFile = os.path.join(destDir,filename)
        if '^' in pre:
            pres = pre.split('^')
            if filename.startswith(pres[0]) and pres[1] in filename:
                shutil.copy(tmpFile, destFile)
                loginfo("sendFile:",filename,",to:",destDir)
                bakFile(cfg_dict,filename,tmpFile)
                isInDirDic = True
        elif filename.startswith(pre):
            shutil.copy(tmpFile, destFile)
            loginfo("sendFile:",filename,",to:",destDir)
            bakFile(cfg_dict,filename,tmpFile)
            isInDirDic = True
            
    #不在配置前缀中则直接删掉
    if not isInDirDic:
        if os.path.exists(tmpFile):
            os.remove(tmpFile)
            loginfo("remove_other:",tmpFile)


#备份拆分并删除文件 'backup_dir' in cfg_dict
def bakFile(cfg_dict,filename,tmpFile):
    if 'backup_dir' in cfg_dict:
        hour = datetime.datetime.now().strftime('%Y%m%d%H')
        backupDir = os.path.join(cfg_dict['backup_dir'],hour)
        if not os.path.exists(backupDir):
            os.mkdir(backupDir)
        bakFile = os.path.join(backupDir,filename)
        shutil.copy(tmpFile, bakFile)
        
    #拆分
    if cfg_dict.get('split_dir'):
        splitDir = cfg_dict['split_dir']
        if not os.path.exists(splitDir):
            os.mkdir(splitDir)
        splitFile = os.path.join(splitDir,filename)
        splitCmd = 'split -l %s %s %s.SPLIT.' % (cfg_dict['split_size'],tmpFile,splitFile)
        os.popen(splitCmd)
        
    os.remove(tmpFile)
    loginfo("remove:",tmpFile)

def main():
    cfg_dict,dirDic = getCfg('prefile.cfg')
    #多线程
    if 'process' in cfg_dict:
        pass
    #连接下载文件
    if 'ip_addr' in cfg_dict:
        getRemoteFile(cfg_dict,dirDic)
    else:
        #临时文件夹发送到正式文件夹
        while 1:
            fileList = os.listdir(cfg_dict['origin_dir'])
            if len(fileList) > 0:
                for fname in fileList:
                    sendFile(cfg_dict,dirDic,fname)
            else:
                time.sleep(int(cfg_dict['scan_time']))

#程序入口
if __name__ == '__main__':
    main()