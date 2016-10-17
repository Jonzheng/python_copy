#!/usr/bin/python
# -*- coding:utf-8 -*-

'''
文件拷贝脚本
2016.10.10
jonzheng
'''

import ConfigParser
import string, os, sys, shutil
import paramiko
import re
import time,datetime

#读取配置
def getCfg():
    cfgfile = 'getdata.cfg'
    cfg_dict = {}
    cf = ConfigParser.ConfigParser()
    cf.read(cfgfile)
    for kv in cf.items(sys.argv[1]):
        cfg_dict[kv[0]] = kv[1]
    return cfg_dict

#拷贝文件
def getFile():
    cfg_dict = getCfg()
    loginfo("start_copy_",sys.argv[1],"_data...")
    file_prefix_list = cfg_dict['file_prefix'].split(",")
    dest_dir_list = cfg_dict['dest_dir'].split(",")
    instr_list = []
    if cfg_dict.get('instr'):
        instr_list = cfg_dict.get('instr').split(",")
    max_file = int(cfg_dict['max_file'])
    #本地拷贝模式
    if cfg_dict.get("ip_addr") == None:
        while True:
            time.sleep(int(cfg_dict['scan_time']))
            file_list = []
            origin_file_list = os.listdir(cfg_dict['origin_dir'])
            if len(origin_file_list) > 0:
                minute = datetime.datetime.now().strftime('%M')
                last_month = (datetime.date(datetime.date.today().year,datetime.date.today().month,1)-datetime.timedelta(1)).strftime('%Y%m')
                for fname in origin_file_list:
                    origin_file = os.path.join(cfg_dict['origin_dir'],fname)
                    if os.path.isdir(origin_file):
                        continue
                    if last_month in fname:
                        os.remove(origin_file)
                        loginfo("last month origin_file is deleted:",fname)
                        continue
                        
                    #遍历文件前缀，拷贝到对应的目标目录
                    for index,file_prefix in enumerate(file_prefix_list):
                        instr = file_prefix
                        if instr_list:
                            instr = instr_list[index] if instr_list[index] else file_prefix
                        if fname.startswith(file_prefix) and instr in fname:
                            dest_dir = dest_dir_list[index]
                            if not os.path.exists(dest_dir):
                                os.mkdir(dest_dir)
                            dest_file = os.path.join(dest_dir,fname)
                            dest_len = len(os.listdir(dest_dir))
                            while minute >= cfg_dict['minute']:
                                loginfo("getdata.py is started but not copy file while minute >=",cfg_dict['minute'])
                                time.sleep(int(cfg_dict['wait_time']))
                                minute = datetime.datetime.now().strftime('%M')
                                
                            while dest_len >= max_file:
                                loginfo("the dest_dir files is gt_",max_file,",_dest_len:",dest_len)
                                time.sleep(int(cfg_dict['wait_time']))
                                dest_len = len(os.listdir(cfg_dict['dest_dir']))
                                
                            if cfg_dict.get('backup_dir'):
                                hour = datetime.datetime.now().strftime('%Y%m%d%H')
                                backup_dir = os.path.join(cfg_dict['backup_dir'],hour)
                                if not os.path.exists(backup_dir):
                                    os.mkdir(backup_dir)
                                backup_file = os.path.join(backup_dir,fname)
                                
                                if cfg_dict['get_way'] == "mv":
                                    shutil.copy(origin_file,backup_file)
                                    shutil.copy(origin_file,dest_file)
                                    loginfo("move_",fname,"_to:",dest_dir_list[index])
                                    os.remove(origin_file)
                            #no backup
                            else:
                                if cfg_dict['get_way'] == "mv":
                                    shutil.copy(origin_file,dest_file)
                                    loginfo("move_",fname,"_to:",dest_dir_list[index])
                                    os.remove(origin_file)
                                    
                            if cfg_dict.get('split_dir'):
                                if not os.path.exists(cfg_dict['split_dir']):
                                    os.mkdir(cfg_dict['split_dir'])
                                split_file = os.path.join(cfg_dict['split_dir'],fname)
                                split_cmd = 'split -l %s %s %s.SPLIT.' % (cfg_dict['split_size'],dest_file,split_file)
                                os.popen(split_cmd)
                                os.remove(dest_file)
                                
                    #拷贝完一次匹配的文件则删除其他不匹配的文件，如果有
                    if os.path.exists(origin_file):
                        os.remove(origin_file)
                        loginfo("remove_other:",origin_file)
                        
    #远程拷贝模式
    elif cfg_dict.get("ip_addr"):
        t = paramiko.Transport((cfg_dict['ip_addr'], int(cfg_dict['port'])))
        try:
            t.connect(username = cfg_dict['username'] , password = cfg_dict['password'])
            sftp = paramiko.SFTPClient.from_transport(t)
            while True:
                time.sleep(int(cfg_dict['scan_time']))
                origin_file_list = sftp.listdir(cfg_dict['origin_dir'])
                if len(origin_file_list) > 0:
                    for fname in origin_file_list:
                        origin_file = os.path.join(cfg_dict['origin_dir'],fname)
                        for index,file_prefix in enumerate(file_prefix_list):
                            if fname.startswith(file_prefix):
                                dest_dir = dest_dir_list[index]
                                if not os.path.exists(dest_dir):
                                    os.mkdir(dest_dir)
                                dest_file = os.path.join(dest_dir,fname)
                                
                                if cfg_dict.get('backup_dir'):
                                    hour = datetime.datetime.now().strftime('%Y%m%d%H')
                                    backup_dir = os.path.join(cfg_dict['backup_dir'],hour)
                                    if not os.path.exists(backup_dir):
                                        os.mkdir(backup_dir)
                                    backup_file = os.path.join(backup_dir,fname)
                                    if cfg_dict['get_way'] == "mv":
                                        sftp.get(origin_file, backup_file)
                                        shutil.copy(backup_file, dest_file)
                                        loginfo("move_",fname,"_to:",dest_dir_list[index])
                                        sftp.remove(origin_file)
                                #no backup
                                else:
                                    if cfg_dict['get_way'] == "mv":
                                        sftp.get(origin_file, dest_file)
                                        loginfo("move_",fname,"_to:",dest_dir_list[index])
                                        sftp.remove(origin_file)
                                if cfg_dict.get('split_dir'):
                                    if not os.path.exists(cfg_dict['split_dir']):
                                        os.mkdir(cfg_dict['split_dir'])
                                    split_file = os.path.join(cfg_dict['split_dir'],fname)
                                    split_cmd = 'split -l %s %s %s.SPLIT.' % (cfg_dict['split_size'],dest_file,split_file)
                                    os.popen(split_cmd)
                                    os.remove(dest_file)

        except(IOError,UnboundLocalError):
            t.close()
            loginfo("IOError,UnboundLocalError,python stopped")
            exit(-1)
        t.close()

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

#程序入口
if __name__ == '__main__':
    getFile()