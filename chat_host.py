import socket
import threading
import time

host = '192.168.254.52'
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

#list of clients
clients = []

#user names
#parallel array to clients
names = []

#stores users time of most recent message sent
lastActivity = []

#stores users busy status
imgReceived = []

#send message to all clients
#assume that the message is already encoded!
def flood(message, excludedClient = None):
    for client in clients:
        if excludedClient == None or excludedClient.getpeername()[1] != client.getpeername()[1]:
            client.send(message)

#Send image to a client
def sendImageTo(image, length, senderName, client):
    
    #send an image sending request to client with image byte length
    msg = 'imgSent' + str(length)
    client.send(msg.encode())

    #Wait for user to receive image send request
    while not imgReceived[clients.index(client)]:
        () #wait
    imgReceived[clients.index(client)] = False

    #send image
    client.sendall(image)


#recieve image from a client and direct to correct sender
def handleImage(client, sendingClient = None):
    #Get the length of the image
    length = int(str(client.recv(1024).decode()))
    data = b''
    #Acknowledge length
    ack = 'ackImgLength'
    client.send(ack.encode())

    #Recieve data
    while True:
        bytes = client.recv(1024)
        data += bytes
        
        if len(data) == length:
            break
     
    #return name of sender client
    name = names[clients.index(client)]
    
    #Send to all clients
    for tempClient in clients:
        if sendingClient == None and tempClient.getpeername()[1] != client.getpeername()[1]:
            thread = threading.Thread(target = sendImageTo, args = (data,length,name,tempClient))
            thread.start()
        elif sendingClient != None and sendingClient.getpeername()[1] == tempClient.getpeername()[1]: 
            thread = threading.Thread(target = sendImageTo, args = (data,length,name,tempClient))
            thread.start()
        
#send to specific client
def send(message, receivingClient):
    receivingClient.send(message)

#handle incoming messages from each client
def manageClient(client):
    while True:
        lastActivity[clients.index(client)] = time.time()
        try:
            message = client.recv(1024)
            #image is about to be sent
            if message.decode() == 'img':
                ack = 'ackImgReq'
                client.send(ack.encode())
                handleImage(client)
            #image is ready to be received
            elif message.decode() == 'imgRec':
                imgReceived[clients.index(client)] = True
            elif len(str(message.decode())) > 2 and message.decode()[:2] == 'pm':
                try:
                    index = names.index(str(message.decode()[2:]))
                    receiver = clients[index]
                    usr = 'usrFound'
                    client.send(usr.encode())
                    usrmessage = client.recv(1024) 
                    send(usrmessage, receiver)

                except:
                    err = 'noUser'
                    client.send(err.encode())
            else:
                flood(message, client)
            
            #send message to all other clients
            
        except:
            #error, remove client
            removeClient(client)
    
    
def removeClient(client):
    index = clients.index(client)   #get index of client
    clients.remove(client)
    name = names[index]
    names.remove(name)
    imgReceived.remove(imgReceived[index])
    lastActivity.remove(lastActivity[index])
    client.close()
    
    #tell other clients who has left
    leavingMessage = name + ' has left the chat room!'
    flood(leavingMessage.encode())

def timeoutLoop():
    while True:
        current_time = time.time()
        #timeout is for 10 minutes
        timeout = 600

        #Check every client for their activity
        for client in clients:
            index = clients.index(client)
            #if last time they were active was longer than timeout kick them
            if current_time - lastActivity[index] > timeout:
                kickMsg = 'inactive'
                client.send(kickMsg.encode())
                removeClient(client)

#Start loop to check for inactivity
thread = threading.Thread(target = timeoutLoop)
thread.start()

#this loop is for accepting multiple client connections
while True:    
    client, addr = server.accept()
    
    #prompts client for name
    client.send('name?'.encode())
    
    name = client.recv(1024).decode()
    clients.append(client)
    names.append(name)
    imgReceived.append(False)
    lastActivity.append(time.time())

    #notify all users when a new person joins
    joinMessage = name + ' has joined the chat room!'
    
    client.send('Welcome to chat room'.encode())
    flood(joinMessage.encode(), client)
    
    
    print('got connection from', client.getpeername())
    
    #create new thread for each client
    thread = threading.Thread(target = manageClient, args = (client,))
    thread.start()
