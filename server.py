import socket,threading,time,re,os
names={}
clients={}
Host=''# change it to your own ip
Port=1112
r_lock=threading.Lock()
def getprest():
    return time.strftime('[%Y.%m.%d  %H:%M:%S]',time.localtime(time.time()))
def acceptfile():
    r_lock.acquire()
    client_file,addr=file_socket.accept();addr=addr[0]
    fname,size=client_file.recv(1024).decode().split('\x00');size=int(size)
    if size>209715200:
        client_file.send('rejected'.encode())
        r_lock.release()
        return
    client_file.send('confirmed'.encode())
    xx=os.open('temp/%s.temp'%fname,os.O_BINARY|os.O_WRONLY|os.O_CREAT)
    client_file.settimeout(10)
    while os.lseek(xx,0,1)!=size:
        try:os.write(xx,client_file.recv(8192))
        except:
            os.close(xx)
            r_lock.release()
            return
    os.close(xx)
    try:os.remove('files/%s'%fname)
    except:pass
    os.rename('temp/%s.temp'%fname,'files/%s'%fname)
    broadcast(clients[names[addr]],'%s %s:\nuploaded file %s\n'%(getprest(),names[addr],fname))
    r_lock.release()
def sendnames():
    client_file,_=name_socket.accept()
    client_file.send('\x00'.join(os.listdir('files')).encode())
def sendfile():
    client_file,addr=send_socket.accept();addr=addr[0]
    fname=client_file.recv(1024).decode()
    size=os.path.getsize('files/'+fname)
    client_file.send(('%d'%size).encode())
    client_file.recv(10)
    xx=os.open('files/'+fname,os.O_RDONLY|os.O_BINARY)
    for _ in range(size//8192+1):
        while True:
            temp=os.lseek(xx,0,1)
            try:
                client_file.send(os.read(xx,8192))
                break
            except:os.lseek(xx,temp,0)
    os.close(xx)
    clients[names[addr]].send(('file %s downloaded\n'%fname).encode())
def handle_client(client_socket,addr):
    name=names[addr]
    print('%s\nClient connected: %s\n'%(getprest(),name))
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
                elif temp[0]=='Chris' and temp[1]=='\x01':
                    threading.Thread(target=sendnames,daemon=True).start()
                elif temp[0]=='Chris' and temp[1]=='\x02':
                    threading.Thread(target=sendfile,daemon=True).start()
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
    global file_socket,name_socket,send_socket
    file_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
    file_socket.bind((Host,Port+1))
    file_socket.listen(5)
    name_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
    name_socket.bind((Host,Port+2))
    name_socket.listen(5)
    send_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
    send_socket.bind((Host,Port+3))
    send_socket.listen(5)
    while True:
        client_socket,addr=server.accept();addr=addr[0]
        if addr not in names.keys():names[addr]=addr
        clients[names[addr]]=client_socket
        threading.Thread(target=handle_client,args=(client_socket,addr),daemon=True).start()
if __name__=='__main__':
    startup()