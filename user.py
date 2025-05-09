import socket
import threading
import cv2
import numpy as np

name = input("what's your name? ")

host = '192.168.254.52'
port = 5000

img_encoded = None
img_bytes = None

client = socket.socket()
client.connect((host,port))

def sendImage(args):
    if len(args) > 1 or len(args) == 0 : 
        print("Incorrect usage try \"/sendImage (image path)\" use")
        return
    else:
        filePath = args[0]
        #Check file extension
        if filePath[-4:] == '.png':
            img = cv2.imread(filePath)
            img_encoded = cv2.imencode('.png',img)[1]
            
        elif filePath[-4:] == '.jpg':
            img = cv2.imread(filePath)
            img_encoded = cv2.imencode('.png',img)[1]
        else:
            #if not a valid image extension return
            print('Give a valid image file')
            return
        #Get array of bytes from the image
        nparr = np.array(img_encoded)
        img_bytes = nparr.tobytes()
        message = "img"
        
        #Send img process request
        client.send(message.encode())
        #send length of img
        client.send(str(len(img_bytes)).encode())
        #send image
        client.sendall(img_bytes)
        

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
        case "sendImage":
            sendImage(args)
        case _:
            print("Command not found!")
#waits for user input, sends to server when user presses enter    
def send():
    while True:
        text = input('')
        try:
            #Check for command usage and split into args
            words = text.split()
            command = words.pop(0)
            
            if command[0:1] == "/":
                tryCommand(command[1:],words)
            else:
                raise Exception("Not a command")
        except:
            if text != "":
                message = name + ': ' + text
                client.send(message.encode())
        
sendThread = threading.Thread(target=send)
receiveThread = threading.Thread(target=receive)

sendThread.start()
receiveThread.start()
    
