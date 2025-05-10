import socket
import threading
import cv2
import numpy as np

name = input("what's your name? ")
password = ''
if name == 'admin':
    password = input("password? ")
host = '192.168.254.52'
port = 5000

class ImageHandler:
    receivedRequest = False
    receivedLength = False

class PMHandler:
    receivedUser = False
    noUser = False

class ConnectionHandler:
    connected = True
    
class KickHandler:
    noUser = False
    successfulKick = False
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
    
        
#send a private message
def privateMessage(args):
    PMHandler.noUser = False
    PMHandler.receivedUser = False
    if len(args) < 2:
        print("Incorrect usage try \"/pm (user) (message)\"")
    
    #Send server a pm request and the person pm is meant for
    user = args.pop(0)
    sendMsg = 'pm' + user
    
    client.send(sendMsg.encode())
    #Wait to find user
    while not PMHandler.receivedUser:
        if PMHandler.noUser:
            print("No user with that name!")
            PMHandler.noUser = False
            return
    PMHandler.receivedUser = False
    
    #Concatenate name with message
    userMessage = 'PM(' + name + '):'
    for word in args:
        userMessage += ' ' + word
    
    #Send message
    client.send(userMessage.encode())
    
# receives message from server
# also sends user if asked

def receive():
    while ConnectionHandler.connected:
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
            elif msg == 'usrFound':
                PMHandler.receivedUser = True
            elif msg == 'noUser':
                PMHandler.noUser = True
            elif msg == 'inactive':
                print("You were inactive for too long!")
                ConnectionHandler.connected = False
                break
            elif msg == 'adminPass':
                client.send(password.encode())
            elif msg == 'WrongAuth':
                print("Wrong password for the admin account")
                ConnectionHandler.connected = False
                break
            elif msg == 'cannotFindUser':
                print("Could not find that user!")
            elif msg == 'kicked':
                print("You have been kicked from the server")
                ConnectionHandler.connected = False
                break
            elif msg == 'noPerm':
                print("You do not have permissions to run this command!")
            elif msg == 'kickSuccessful':
                KickHandler.successfulKick = True
            elif msg == 'noUserKick':
                KickHandler.noUser = True
            else:
                print(msg)
            
        except:
            client.close()
            break

#kick a user
def kickUser(args):
    KickHandler.noUser = False
    KickHandler.successfulKick = False
    #Check permissions, permissions also checked on server side
    if name != 'admin':
        print("No permission!")
        return
    
    if len(args) == 0 or len(args) > 1:
        print("Incorrect usage try \"/kick (user)\"")
    
    msg = 'kick' + args[0]
    client.send(msg.encode())
    
    
    while not KickHandler.successfulKick:
        if KickHandler.noUser:
            print("No user with name: " + args[0])
            KickHandler.noUser = False
            return
    KickHandler.successfulKick = False
    print("Successfully kicked " + args[0])
    

def tryCommand(command, args):
    match command:
        case "sendImage":
            sendImage(args)
        case "pm":
            privateMessage(args)
        case "kick":
            kickUser(args)
        case _:
            print("Command not found!")
#waits for user input, sends to server when user presses enter    
def send():
    while ConnectionHandler.connected:
        text = input('')
        if not ConnectionHandler.connected:
            break
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
    
