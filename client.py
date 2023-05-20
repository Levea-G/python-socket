import socket
import threading
import tkinter as tk
from tkinter import filedialog
import os
Host='2001:da8:8007:4011:642c:fe94:df54:65c7'# change it to the server ip
Port=1112
class chat():
    def __init__(self):
        def addrecord(message):
            self.record.config(state='normal')
            self.record.insert('end',message)
            if sc1.get()[1]==1:self.record.see('end')
            self.record.config(state='disabled')
        def clear():
            self.record.config(state='normal')
            self.record.delete('1.0','end')
            self.record.config(state='disabled')
        def send(_=None):
            global server_socket
            self.msg.delete('%d.end'%(int(self.msg.index('insert')[0])-1))
            message=self.msg.get('1.0','end')
            if len(message)==0 or message=='\n':return
            try:
                server_socket.send(message.encode())
                self.msg.delete(0.0,'end')
            except:pass
        def receive():
            global server_socket
            while True:
                try:message=server_socket.recv(1024).decode()+'\n'
                except:break
                addrecord(message)
        def _sf(path,times):
            file_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
            try:file_socket.connect((Host,Port+1))
            except:return
            file_socket.send(('%s\x00%d'%(path.split('/')[-1],times)).encode())
            file_socket.recv(10)
            xx=os.open(path,os.O_BINARY|os.O_RDONLY)
            for _ in range(times):
                file_socket.send(os.read(xx,8192))
            os.close(xx)
            file_socket.close()
        def sendfile():
            global server_socket
            try:server_socket.getpeername()
            except:return
            for path in filedialog.askopenfilenames():
                times=os.path.getsize(path)//8192+1
                if times>131072:
                    addrecord('file too big(>1G)!\n\n')
                elif len(path.split('/')[-1])>200:
                    addrecord('file name too long(>200)!\n\n')
                else:
                    server_socket.send('/Chris \x00 \n'.encode())
                    threading.Thread(target=_sf,args=(path,times),daemon=True).start()
        def enter(_=None):
            self.msg.insert(self.msg.index('insert'),'')
        def reconnect():
            global server_socket
            try:server_socket.close()
            except:pass
            try:
                server_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
                server_socket.settimeout(2)
                server_socket.connect((Host,Port))
                server_socket.settimeout(None)
                msg='Connected to %s:%d\n\n'%(Host,Port)
                threading.Thread(target=receive,daemon=True).start()
            except:msg='Failed connecting to %s:%d\n\n'%(Host,Port)
            addrecord(msg)
        self.main=tk.Tk()
        self.main.title('chatroom')
        self.main.geometry('640x480+300+200')
        self.record=tk.Text(self.main,font=('times',14),state='disable',wrap='word')
        self.record.place(relx=0.2,rely=0,relwidth=0.8,relheight=0.8)
        sc1=tk.Scrollbar(self.record,command=self.record.yview)
        sc1.pack(side='right',fill='y')
        self.record.config(yscrollcommand=sc1.set)
        self.msg=tk.Text(self.main,font=('times',14),wrap='word')
        self.msg.place(relx=0.2,rely=0.8,relwidth=0.8,relheight=0.2)
        sc2=tk.Scrollbar(self.msg,command=self.msg.yview)
        sc2.pack(side='right',fill='y',in_=self.msg,expand=0)
        self.msg.config(yscrollcommand=sc2.set)
        tk.Button(self.main,font=('times',12),text='clear\nrecord',command=clear).place(relx=0.05,rely=0.2,relwidth=0.12,relheight=0.1)
        tk.Button(self.main,font=('times',12),text='send\nfile',command=sendfile).place(relx=0.05,rely=0.4,relwidth=0.1,relheight=0.1)
        tk.Button(self.main,font=('times',12),text='reconnect',command=reconnect).place(relx=0.05,rely=0.6,relwidth=0.1,relheight=0.1)
        self.main.bind('<Return>',send)
        self.main.bind('<Alt-KeyPress-Return>',enter)
        self.msg.focus();reconnect()
if __name__=='__main__':
    chat().main.mainloop()