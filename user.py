import socket
import threading

name = input("what's your name? ")

host = '192.168.1.130'
port = 5000

client = socket.socket()
client.connect((host,port))

# receives message from server
# also sends user if asked
def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            
            if msg == 'name?':
                client.send(name.encode())

            else:
                print(msg)
            
        except:
            client.close();
            break

#waits for user input, sends to server when user presses enter    
def send():
    while True:
        text = input('')
        message = name + ': ' + text
        client.send(message.encode())
        
sendThread = threading.Thread(target=send)
receiveThread = threading.Thread(target=receive)

sendThread.start()
receiveThread.start()
    