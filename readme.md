脚本功能：
    根据配置拷贝文件，详细查看配置项注释
    
如需测试可以到[eventcenter@132.121.86.54]/data/jonz
将getdata.py与getdata.cfg拷贝至/data/jonz

启动：
    python getdata.py _arg &

查进程：
    ps aux|grep python
    例：8006     52461  1.2  0.0 201056 10736 pts/12   S    22:25   0:00 python getdata.py pre
    最后一个参数对应脚本参数，倒数第二个参数为脚本名称，第二个参数即为进程号

杀进程：
    kill -9 52461

杀进程2：
    需要stop.py脚本，参数为getdata.py对应的输入参数
    python stop.py _arg

查看日志：
    tail -99f _arg.log

_arg 对应.cfg配置文件的标签



