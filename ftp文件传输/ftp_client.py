from socket import *
import os,sys

#具体功能
class FtpClient(object):
    def __init__(self,sockfd):
        self.sockfd=sockfd #套接字属性

    def do_list(self):
        self.sockfd.send(b'L') #发送请求
        #等待回复
        data=self.sockfd.recv(128).decode()
        if data=='ok':
            data=self.sockfd.recv(4096).decode()
            files=data.split(',') #返回列表
            for file in files:
                print(file)
        else:
            #无法完成操作
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self,filename):
        self.sockfd.send(('G '+filename).encode())
        data=self.sockfd.recv(128).decode()
        if data=='ok':
            fd=open(filename,'wb')
            while True:
                data=self.sockfd.recv(1024)
                if data==b'##':
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self,filename):
        try:
            f=open(filename,'rb')
        except IOError:
            print("没有文件")
            return
        #获取真实文件名，对路径解析
        filename=filename.split('/')[-1]
        self.sockfd.send(('P '+filename).encode())
        data=self.sockfd.recv(128).decode()
        if data=='ok':
            while True:
                data=f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            f.close()
        else:
            print(data)

#网络连接
def main():
    #服务端地址
    ADDR=('127.0.0.1',6555)

    sockfd=socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("连接服务器失败",e)
        return

    #创建文件处理类对象
    ftp=FtpClient(sockfd)


    while True:
        print("\n******命令选项******")
        print("***     list      ***")
        print("***   get  file   ***")
        print("***   put  file   ***")
        print("***     quit      ***")
        print("=====================")

        cmd=input("输入命令>>")
        if cmd.strip()=='list':
            ftp.do_list()
        elif cmd.strip()=='quit':
            ftp.do_quit()
        elif cmd[:3]=='get':
            #strip() 去除两边空格
            filename=cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3]=='put':
            filename=cmd.strip().split(' ')[-1]
            ftp.do_put(filename)
        else:
            print("请输入正确命令")


if __name__=="__main__":
    main()