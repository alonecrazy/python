'''
ftp 文件服务器
fork server训练
'''
from socket import *
import os,sys
import signal
import time

#全局变量
HOST='0.0.0.0'
PORT=6555
ADDR=(HOST,PORT)
FILE_PATH='/home/tarena/fly/'

class FtpServer(object):
    def __init__(self,connfd):
        self.connfd=connfd
    
    def do_list(self):
        #获取文件列表
        file_list=os.listdir(FILE_PATH)
        if not file_list:
            self.connfd.send("文件库为空".encode())
        else:
            self.connfd.send(b'ok')
            time.sleep(0.1)

        files=''
        for file in file_list:
            if file[0]!='.' and os.path.isfile(FILE_PATH+file):
                files=files+file+','
        #将拼接好的字符串传给客户端
        self.connfd.send(files.encode())

    def do_get(self,filename):
        try:
            fd=open(FILE_PATH+filename,'rb')
        except IOError:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b'ok')
            time.sleep(0.1)
        #发送文件内容
        while True:
            data=fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

    def do_put(self,filename):
        if os.path.exists(FILE_PATH+filename):
            self.connfd.send('该文件已存在'.encode())
            return
        fd=open(FILE_PATH+filename,'wb')
        self.connfd.send(b'ok')
        #接收文件
        while True:
            data=self.connfd.recv(1024)
            if data==b'##':
                break
            fd.write(data)
        fd.close()

def do_request(connfd):
    ftp=FtpServer(connfd)
    while True:
        data=connfd.recv(1024).decode()
        if not data or data[0]=='Q':
            connfd.close()
            return

        if data[0]=='L':#判断类型,list列表
            ftp.do_list()
        
        elif data[0]=='G':
            filename=data.split(' ')[-1]
            ftp.do_get(filename)

#网络搭建
def main():
    #创建套接字
    sockfd=socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print("Listen the port 6555")
    #防止僵尸进程
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    #循环等待客户端连接
    while True:
        try:
            connfd,addr=sockfd.accept()
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit("服务器退出")
        except Exception as e:
            print("服务器异常",e)
            continue
        print("连接客户端：",addr)

        #创建子进程
        pid=os.fork()
        if pid==0:
            sockfd.close()
            do_request(connfd)#处理客户端请求
            os._exit(0)
            
        else:
            connfd.close()

if __name__=="__main__":
    main()