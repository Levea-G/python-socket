import socket
import threading
import time
import re
names={}
clients={}
Host=''# change it to your own ip
Port=1112
def handle_client(client_socket,addr):
    name=names[addr]
    while True:
        try:
            message,tstamp=client_socket.recv(1024).decode(),time.strftime('[%Y.%m.%d  %H:%M:%S]',time.localtime(time.time()))
            fullmsg='%s %s:\n%s'%(tstamp,name,message)
            print(fullmsg)
            temp=re.findall(re.compile('^/([a-zA-Z]+)[ ]+([^ \n]+)[ ]*(.*)$',re.DOTALL),message)
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
                        name=temp[1]
                elif temp[0]=='tell':
                    if len(temp[1])>20 or temp[1] not in clients.keys():
                        client_socket.send(('%s\nServer: name %s doesn\'t exist\n'%(tstamp,temp[1])).encode())
                    else:
                        clients[temp[1]].send(('%s(SILENT) %s ->\n%s'%(tstamp,name,temp[2])).encode())
                        client_socket.send(('%s(SILENT) -> %s\n%s'%(tstamp,temp[1],temp[2])).encode())
                else:exit(0)
            except:broadcast(client_socket,fullmsg)
        except:break
    try:
        clients.pop(name)
        names[addr]=name
        print('Client disconnected: %s\n'%names[addr])
    except:pass
    client_socket.close()
def broadcast(client_socket,message):
    others=list(clients.values())
    others.remove(client_socket)
    for client in others:
        client.send(message.encode())
    client_socket.send((message[:22]+message[message.find(':\n')+1:]).encode())
def startup():
    #server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server=socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
    server.bind((Host,Port))
    server.listen(5)
    print('Server started on %s:%s at %s\n'%(Host,Port,time.strftime('%Y.%m.%d  %H:%M:%S',time.localtime(time.time()))))
    while True:
        client_socket,addr=server.accept()
        addr=addr[0]
        if addr not in names.keys():names[addr]=addr
        clients[names[addr]]=client_socket
        print('Client connected: %s\n'%names[addr])
        threading.Thread(target=handle_client,args=(client_socket,addr),daemon=True).start()
if __name__=='__main__':
    startup()