import socket
import threading
import time
names={}
clients=[]
Host=''# change it to your own ip
Port=1112
def setname(message,addr):
    temp=message.split(' ')
    if temp[0]=='setname':names[addr]=temp[1].strip()
    return message
def handle_client(client_socket,addr):
    while True:
        try:
            message=setname(client_socket.recv(1024).decode(),addr)
            fullmsg='%s %s:\n%s'%(time.strftime('[%Y.%m.%d  %H:%M:%S]',time.localtime(time.time())),names[addr],message)
            print(fullmsg)
            broadcast(client_socket,fullmsg)
        except:break
    try:
        clients.remove(client_socket)
        print('Client disconnected: %s\n'%names[addr])
    except:pass
    client_socket.close()
def broadcast(client_socket,message):
    others=clients.copy()
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
        clients.append(client_socket)
        addr=addr[0]
        if addr not in names.keys():names[addr]=addr
        print('Client connected: %s\n'%names[addr])
        threading.Thread(target=handle_client,args=(client_socket,addr),daemon=True).start()
if __name__=='__main__':
    startup()
