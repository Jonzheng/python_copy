�ű����ܣ�
    �������ÿ����ļ�����ϸ�鿴������ע��
    
������Կ��Ե�[eventcenter@132.121.86.54]/data/jonz
��getdata.py��getdata.cfg������/data/jonz

������
    python getdata.py _arg &

����̣�
    ps aux|grep python
    ����8006     52461  1.2  0.0 201056 10736 pts/12   S    22:25   0:00 python getdata.py pre
    ���һ��������Ӧ�ű������������ڶ�������Ϊ�ű����ƣ��ڶ���������Ϊ���̺�

ɱ���̣�
    kill -9 52461

ɱ����2��
    ��Ҫstop.py�ű�������Ϊgetdata.py��Ӧ���������
    python stop.py _arg

�鿴��־��
    tail -99f _arg.log

_arg ��Ӧ.cfg�����ļ��ı�ǩ



