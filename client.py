import socket
import threading
import tkinter as tk
from tkinter import filedialog
import os
Host=''
Port=1112
r_lock=threading.Lock()
msg_lock=threading.Lock()
class chat():
    def __init__(self):
        def addrecord(message,typen):
            self.record.config(state='normal')
            if sc1.get()[1]==1:
                self.record.insert('end',message,typen)
                self.record.see('end')
            else:self.record.insert('end',message,typen)
            self.record.config(state='disabled')
        def clear():
            self.record.config(state='normal')
            self.record.delete('1.0','end')
            self.record.config(state='disabled')
        def send(_=None):
            self.msg.delete('%d.end'%(int(self.msg.index('insert')[0])-1))
            message=self.msg.get('1.0','end')
            if len(message)==0 or message=='\n':return
            try:
                server_socket.send(message.encode())
                self.msg.delete(0.0,'end')
            except:pass
        def receive():
            while True:
                try:message=server_socket.recv(1024).decode()
                except:break
                msg_lock.acquire()
                if message!='\x00':
                    if message[0]=='m':addrecord(message[1:]+'\n','me')
                    elif message[0]=='p':addrecord(message[1:]+'\n','private')
                    elif message[0]=='g':addrecord(message[1:]+'\n','silent')
                    else:addrecord(message+'\n','others')
                msg_lock.release()
        def _sf(path,size):
            file_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
            try:file_socket.connect((Host,Port+1))
            except:return
            file_socket.send(('%s\x00%d'%(path.split('/')[-1],size)).encode())
            reply=file_socket.recv(10).decode()
            if reply=='rejected':
                addrecord('server rejected\n\n','me')
                file_socket.close()
                return
            xx=os.open(path,os.O_BINARY|os.O_RDONLY)
            for _ in range(size//8192+1):
                while True:
                    temp=os.lseek(xx,0,1)
                    try:
                        file_socket.send(os.read(xx,8192))
                        break
                    except:os.lseek(xx,temp,0)
            os.close(xx)
            file_socket.close()
        def send_file():
            try:server_socket.getpeername()
            except:return
            for path in filedialog.askopenfilenames():
                size=os.path.getsize(path)
                if size>209715200:
                    addrecord('file too big(>200M)!\n\n','private')
                elif len(path.split('/')[-1])>200:
                    addrecord('file name too long(>200)!\n\n','private')
                else:
                    msg_lock.acquire()
                    server_socket.send(('/Chris \x00 upload %s\n'%path.split('/')[-1]).encode())
                    msg_lock.release()
                    threading.Thread(target=_sf,args=(path,size),daemon=True).start()
        def get_file():
            try:server_socket.getpeername()
            except:return
            def refresh():
                server_socket.send('/Chris \x01 asknames\n'.encode())
                file_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
                file_socket.connect((Host,Port+2))
                fnames=file_socket.recv(1024).decode().split('\x00')
                file_socket.close()
                nms.delete(0,'end')
                for item in fnames:nms.insert('end',item)
            def _gf(path,fname):
                try:xx=os.open(path,os.O_BINARY|os.O_WRONLY|os.O_CREAT)
                except:return
                r_lock.acquire()
                file_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
                file_socket.connect((Host,Port+3))
                file_socket.send(fname.encode())
                size=int(file_socket.recv(1024).decode())
                file_socket.send('confirmed'.encode())
                file_socket.settimeout(10)
                while os.lseek(xx,0,1)!=size:
                    try:os.write(xx,file_socket.recv(8192))
                    except:
                        os.close(xx)
                        file_socket.close()
                        r_lock.release()
                        return
                os.close(xx)
                file_socket.close()
                r_lock.release()
            def getfile():
                fname=nms.get('active')
                if fname=='':return
                path=filedialog.asksaveasfilename(initialfile=fname)
                server_socket.send(('/Chris \x02 download %s\n'%fname).encode())
                threading.Thread(target=_gf,args=(path,fname),daemon=True).start()
                checklist.focus()
            checklist=tk.Toplevel()
            checklist.title('file list')
            checklist.geometry('640x480+350+250')
            checklist.resizable(0,0)
            nms=tk.Listbox(checklist)
            nms.place(relx=0,rely=0,relwidth=1,relheight=0.8)
            scy=tk.Scrollbar(nms,command=nms.yview)
            scx=tk.Scrollbar(nms,command=nms.xview,orient='horizontal')
            scy.pack(side='right',fill='y')
            scx.pack(side='bottom',fill='x')
            nms.config(yscrollcommand=scy.set,xscrollcommand=scx.set)
            tk.Button(checklist,font=('times',12),text='get',command=getfile).place(relx=0.3,rely=0.85,relwidth=0.1,relheight=0.05)
            tk.Button(checklist,font=('times',12),text='refresh',command=refresh).place(relx=0.6,rely=0.85,relwidth=0.1,relheight=0.05)
            refresh()
            checklist.transient()
        def enter(_=None):
            self.msg.insert(self.msg.index('insert'),'')
        def reconnect():
            global server_socket
            try:server_socket.close()
            except:pass
            try:
                Host=socket.getaddrinfo('',None,socket.AF_INET6)[2][4][0]#input hostname
                server_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
                server_socket.settimeout(2)
                server_socket.connect((Host,Port))
                server_socket.settimeout(None)
                threading.Thread(target=receive,daemon=True).start()
            except:addrecord('Failed to connect to server\n\n','private')
        self.main=tk.Tk()
        self.main.title('chatroom')
        self.main.geometry('640x480+300+200')
        self.record=tk.Text(self.main,font=('times',14),state='disable',wrap='word')
        self.record.place(relx=0.2,rely=0,relwidth=0.8,relheight=0.8)
        sc1=tk.Scrollbar(self.record,command=self.record.yview)
        sc1.pack(side='right',fill='y')
        self.record.config(yscrollcommand=sc1.set)
        #
        self.record.tag_add('me','0.0')
        self.record.tag_config('me',foreground='blue')
        self.record.tag_add('others','0.0')
        self.record.tag_config('others',foreground='black')
        self.record.tag_add('private','0.0')
        self.record.tag_config('private',foreground='purple')
        self.record.tag_add('silent','0.0')
        self.record.tag_config('silent',foreground='grey')
        #
        self.msg=tk.Text(self.main,font=('times',14),wrap='word')
        self.msg.place(relx=0.2,rely=0.8,relwidth=0.8,relheight=0.2)
        sc2=tk.Scrollbar(self.msg,command=self.msg.yview)
        sc2.pack(side='right',fill='y',in_=self.msg,expand=0)
        self.msg.config(yscrollcommand=sc2.set)
        #
        tk.Button(self.main,font=('times',12),text='clear\nrecord',command=clear).place(relx=0.05,rely=0.12,relwidth=0.1,relheight=0.1)
        tk.Button(self.main,font=('times',12),text='send\nfile',command=send_file).place(relx=0.05,rely=0.34,relwidth=0.1,relheight=0.1)
        tk.Button(self.main,font=('times',12),text='get\nfile',command=get_file).place(relx=0.05,rely=0.56,relwidth=0.1,relheight=0.1)
        tk.Button(self.main,font=('times',12),text='reconnect',command=reconnect).place(relx=0.05,rely=0.78,relwidth=0.1,relheight=0.1)
        #
        self.main.bind('<Return>',send)
        self.main.bind('<Alt-KeyPress-Return>',enter)
        self.msg.focus();reconnect()
if __name__=='__main__':
    chat().main.mainloop()
