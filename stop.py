#!/usr/bin/python2
import os,sys

prc = 'ps aux | grep python'
txt = os.popen(prc).readlines()

for line in txt:
    colum = line.split()
    pid = colum[1]
    name = colum[-2]
    arg = colum[-1]
    if name == "getdata.py" and arg == sys.argv[1]:
        #print pid,colum
        pkill = 'kill -9 '+pid
        os.popen(pkill)
    
#ps aux|grep python|awk '{$13}'/_arg_/ | awk '{print $2}'| xargs kill -9