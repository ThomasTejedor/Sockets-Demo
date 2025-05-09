import socket
import threading

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

#send message to all clients
#assume that the message is already encoded!
def flood(message, excludedClient = None):
    for client in clients:
        if excludedClient == None or excludedClient.getpeername()[1] != client.getpeername()[1]:
            client.send(message)
            
def handleImage(client, excludedClient = None):
    #Get the length of the image
    length = int(str(client.recv(1024).decode()))
    data = b''
    
    while len(data) < length:
        bytes = client.recv(1024)
        data += bytes
    
    for tempClient in clients:
        if excludedClient == None or excludedClient.getpeername()[1] != client.getpeername()[1]:
            tempClient.send("testing")
#send to specific client
#def send(message, client):

#handle incoming messages from each client
def manageClient(client):
    while True:
        try:
            message = client.recv(1024)
            if message.decode() == 'img':
                handleImage(client)
            else:
                flood(message)
            
            #send message to all other clients
            
        except:
            #error, remove client
            removeClient(client)
    
    
def removeClient(client):
    index = clients.index(client)   #get index of client
    clients.remove(client)
    name = names[index]
    names.remove(name)
    client.close()
    
    #tell other clients who has left
    leavingMessage = name + ' has left the chat room!'
    flood(leavingMessage.encode())

#this loop is for accepting multiple client connections
while True:    
    client, addr = server.accept()
    
    #prompts client for name
    client.send('name?'.encode())
    
    name = client.recv(1024).decode()
    clients.append(client)
    names.append(name)
    
    #notify all users when a new person joins
    joinMessage = name + ' has joined the chat room!'
    
    client.send('Welcome to chat room'.encode())
    flood(joinMessage.encode(), client)
    
    
    print('got connection from', client.getpeername())
    
    #create new thread for each client
    thread = threading.Thread(target = manageClient, args = (client,))
    thread.start()
