import socket
import threading
import tkinter as tk
Host='192.168.124.15'
Port=1112
def receive_msg(client_socket,chats):
    while True:
        try:message=client_socket.recv(1024).decode()
        except:
            message='Disconnected from server'
            break
        chats.record.config(state='normal')
        chats.record.insert('end',message+'\n')
        chats.record.see('end')
        chats.record.config(state='disabled')
class chat():
    def __init__(self):
        def clear():
            self.record.config(state='normal')
            self.record.delete(0.0,'end')
            self.record.config(state='disabled')
        def send(_=None):
            global client_socket
            self.msg.delete('%d.end'%(int(self.msg.index('insert')[0])-1))
            message=self.msg.get('1.0','end')
            if len(message)==0 or message=='\n':return
            client_socket.send(message.encode())
            self.msg.delete(0.0,'end')
        def enter(_=None):
            self.msg.insert(self.msg.index('insert'),'')
        def reconnect():
            global client_socket
            try:
                client_socket.connect((Host,Port))
                msg='Connected to %s:%d\n\n'%(Host,Port)
                threading.Thread(target=receive_msg,args=(client_socket,self),daemon=True).start()
            except:msg='Failed connecting to %s:%d\n\n'%(Host,Port)
            self.record.config(state='normal')
            self.record.insert('end',msg)
            self.record.see('end')
            self.record.config(state='disabled')
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
        tk.Button(self.main,font=('times',12),text='reconnect',command=reconnect).place(relx=0.05,rely=0.6,relwidth=0.1,relheight=0.1)
        self.main.bind('<Return>',send)
        self.main.bind('<Alt-KeyPress-Return>',enter)
        self.msg.focus();reconnect()
if __name__=='__main__':
    client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    chat().main.mainloop()