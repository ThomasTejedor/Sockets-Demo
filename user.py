import socket
import threading
import cv2
import numpy as np

name = input("what's your name? ")

host = '192.168.254.52'
port = 5000

class ImageHandler:
    receivedRequest = False
    receivedLength = False

client = socket.socket()
client.connect((host,port))



def sendImage(args):
    ImageHandler.receivedRequest = False
    ImageHandler.receivedLength = False
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
        message = 'img'
        
            
        client.send(message.encode())
        while not ImageHandler.receivedRequest:
            ()
        #send length of img
        client.send(str(len(img_bytes)).encode())
        
        while not ImageHandler.receivedLength:
            ()
            
        #send image
        client.sendall(img_bytes)

#Displays image from buffer
def displayImage(image):
    nparr = np.frombuffer(image,np.byte)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow("cpp image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
#Receives image from server then handles the data
def receiveImage(length):
    #Let server know you are ready to receive image data
    msg = 'imgRec'
    client.send(msg.encode())
    
    data = b''
    #receive image from server
    while True:
        bytes = client.recv(1024)
        data += bytes
        
        if(len(data)) == length:
            break
    
    thread = threading.Thread(target = displayImage, args=(data,))
    thread.start()
    
    
    
# receives message from server
# also sends user if asked

def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg == 'name?':
                client.send(name.encode())
            #acknowledge server received image request
            elif msg == 'ackImgReq':
                ImageHandler.receivedRequest = True
            #acknowledge server received length
            elif msg == 'ackImgLength':
                ImageHandler.receivedLength = True
            #If an img is being sent to user
            elif len(msg) > 7 and msg[:7] == 'imgSent':
                receiveImage(int(msg[7:]))
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
    
