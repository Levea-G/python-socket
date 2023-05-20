import socket
import threading
import time
import re
import os
names={}
clients={}
Host=''# change it to your own ip
Port=1112
lock=threading.Lock()
def getprest():
    return time.strftime('[%Y.%m.%d  %H:%M:%S]',time.localtime(time.time()))
def acceptfile():
    lock.acquire()
    client_file,addr=file_socket.accept();addr=addr[0]
    fname,size=client_file.recv(1024).decode().split('\x00');size=int(size)
    client_file.send('received'.encode())
    xx=os.open('temp/%s.temp'%fname,os.O_BINARY|os.O_WRONLY|os.O_CREAT)
    client_file.settimeout(10)
    while os.lseek(xx,0,1)!=size:
        try:os.write(xx,client_file.recv(8192))
        except:return
    os.close(xx)
    try:os.remove('files/%s'%fname)
    except:pass
    os.rename('temp/%s.temp'%fname,'files/%s'%fname)
    broadcast(clients[names[addr]],'%s %s:\nuploaded file %s\n'%(getprest(),names[addr],fname))
    lock.release()
def handle_client(client_socket,addr):
    name=names[addr]
    while True:
        try:
            message,tstamp=client_socket.recv(1024).decode(),getprest()
            fullmsg='%s %s:\n%s'%(tstamp,name,message)
            print(fullmsg)
            temp=re.findall(re.compile('^/([a-zA-Z]+)[ ]*([^ \n]*)[ ]*(.*)$',re.DOTALL),message)
            try:
                temp=temp[0]
                if temp[0]=='setname':
                    if len(temp[1])>20:
                        client_socket.send(('%s\nServer: name %s is too long(>20)!\n'%(tstamp,temp[1])).encode())
                    elif temp[1] in clients.keys():
                        client_socket.send(('%s\nServer: name %s already exists\n'%(tstamp,temp[1])).encode())
                    else:
                        broadcast(client_socket,'%s %s:\nsetname -> %s\n'%(tstamp,name,temp[1]))
                        clients[temp[1]]=clients.pop(name)
                        names[addr]=name=temp[1]
                elif temp[0]=='tell':
                    if len(temp[1])>20 or temp[1] not in clients.keys():
                        client_socket.send(('%s\nServer: name %s doesn\'t exist\n'%(tstamp,temp[1])).encode())
                    else:
                        clients[temp[1]].send(('%s(SILENT) %s ->\n%s'%(tstamp,name,temp[2])).encode())
                        client_socket.send(('%s(SILENT) -> %s\n%s'%(tstamp,temp[1],temp[2])).encode())
                elif temp[0]=='member':
                    client_socket.send((tstamp+'\n'+'\n'.join(names.values())+'\n').encode())
                elif temp[0]=='Chris' and temp[1]=='\x00':
                    threading.Thread(target=acceptfile,daemon=True).start()
                else:exit(0)
            except:broadcast(client_socket,fullmsg)
        except:break
    try:
        clients.pop(name)
        print('%s\nClient disconnected: %s\n'%(getprest(),names[addr]))
    except:pass
    client_socket.close()
def broadcast(client_socket,message):
    others=list(clients.values())
    others.remove(client_socket)
    for client in others:
        client.send(message.encode())
    if client_socket:client_socket.send((message[:22]+message[message.find(':\n')+1:]).encode())
def startup():
    try:os.mkdir('temp')
    except:pass
    try:os.mkdir('files')
    except:pass
    server=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
    server.bind((Host,Port))
    server.listen(5)
    print('%s\nServer started on %s:%s\n'%(getprest(),Host,Port))
    global file_socket
    file_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
    file_socket.bind((Host,Port+1))
    file_socket.listen(5)
    while True:
        client_socket,addr=server.accept();addr=addr[0]
        if addr not in names.keys():names[addr]=addr
        clients[names[addr]]=client_socket
        print('%sClient connected: %s\n'%(getprest(),names[addr]))
        threading.Thread(target=handle_client,args=(client_socket,addr),daemon=True).start()
if __name__=='__main__':
    startup()