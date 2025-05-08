import socket
import threading

name = input("what's your name? ")

host = '192.168.254.52'
port = 5000

client = socket.socket()
client.connect((host,port))

def sendImage():
    if len(args) > 1 or len(args) == 0 : 
        print("Incorrect usage try \"/SendImage (image path)\" use")
        return
    
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
            client.close()
            break

def tryCommand(command, args):
    match command:
        case "SendImage":
            sendImage(args)
        case _:
            print("Command not found!")
#waits for user input, sends to server when user presses enter    
def send():
    while True:
        text = input('')
        try:
            words = text.split()
            if words[0].substring(0,1) == "/":
                tryCommand(words.substring(1),words.pop(0))
        except:
            if text != "":
                message = name + ': ' + text
                client.send(message.encode())
        
sendThread = threading.Thread(target=send)
receiveThread = threading.Thread(target=receive)

sendThread.start()
receiveThread.start()
    
