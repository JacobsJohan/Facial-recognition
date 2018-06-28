#imports of needed packages
import os
import sys
import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from PIL import Image
import threading
from queue import Queue

#import sendMail
import smtplib
# MIME = Multipurpose Internet Mail Extensions
# MIME legt de structuur en codering van e-mailberichten vast.
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import sched

#Global declarations
camera=PiCamera()
FPS=5
nrOfPics=0
mailFlag=0

#Choose classifier detector
##In case we use haarcascades (more accurate)
detector=cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
##In case we use LBP(faster)
#detector=cv2.CascadeClassifier('/home/pi/opencv/data/lpbcascades/lpbcascade_frontalface_improved.xml')

#Choose recognizer
##create LBPH recognizer 
recognizer = cv2.face.LBPHFaceRecognizer_create()

##or use EigenFaceRecognizer
###face_recognizer = cv2.face.EigenFaceRecognizer_create()

##or use FisherFaceRecognizer
###face_recognizer = cv2.face.FisherFaceRecognizer_create()

#recognizer.read('/home/pi/Documents/Facial recog/recognizer/trainingData.yml')
font = cv2.FONT_HERSHEY_PLAIN


#For threading and flowcontrol
interrupt=False
running=True

class currentFrame:
    def __init__(self):
        self.frame = None
        self.name = None
        self.cert = None


cF = currentFrame()


def makeChoice():
    try:
        choice = int(input("Choose what you want to do: \nRecognize new face: 1 \nRun trainer: 2 \nContinuous recognition: 3 \n"))
    except:
        print("Invalid input")
        choice = int(input("Choose what you want to do: \nRecognize new face: 1 \nRun trainer: 2 \nContinuous recognition: 3 \n"))
    return choice

# Functions needed for building the database
def nameMapping(name=None):

    if name is None:
        name = ("Enter your name: ")

    #In case the file does not exist we need to open it in a different way (opening with append+ will create it first)
    try:
        f = open('mapping.txt','r+')
    except:
        f = open('mapping.txt','a+')
    userID = 1 #Needs to be initialized in case file is empty
    newName = True
    for line in f:
        #print(line)
        if (line.split('.')[0] == name):
            userID = int(line.split('.')[1])
            newName = False
            break
        else:
            userID = userID+1
    if (newName):
        f.write(name+'.'+str(userID)+'\n')
    #print(userID)
    f.close()
    return name, userID

s = sched.scheduler(time.time, time.sleep)

def mailSched():
    s.enter(10,1,mailHandler)
    s.run()

def mailHandler():
    global mailFlag
    if mailFlag:
        sendMail()
        mailFlag = 0

def makeDir(path):
    directory = os.path.dirname(path)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)

def newRecognition(name=None):
    #Initializing camera and grab a reference to the raw camera capture
    #camera=PiCamera()
    global camera
    global interrupt
    interrupt=False
    #Adjusting some properties
    camera.resolution=(640,480)
    camera.framerate=30
    #This function creates a 3D RGB-array from a RGB capture
    rawCapture=PiRGBArray(camera)

    #Allow camera to initialize. Not really necessary but can't hurt.
    time.sleep(0.1)
    #Input an Id to be linked to.
    name, userID = nameMapping(name)
    #SampleNum to let program exit inf loop
    sampleNum=0

    #Capture frames from camera
    for frame in camera.capture_continuous(rawCapture,format='bgr'):
        #Grab NumPy array from image
        img=frame.array

        #Show the unprocessed frame
        #cv2.imshow("Imag",img)
        key=cv2.waitKey(1)&0xFF

        
        sampleNum=sampleNum+1

        #Convert RGB to grayscale
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #Detect faces
        faces= detector.detectMultiScale(gray,1.3,5)

        #Draw a rectangle around every face
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            #Write image to folder containing images
            writePath = '/home/pi/Documents/Facial recog/DataSet/'+name+'/'
            #print(writePath)
            makeDir(writePath)
            cv2.imwrite(writePath+name+'.'+str(userID)+'.'+str(sampleNum)+'.jpg',gray[y:y+h,x:x+w])
            
        cv2.imshow('frame',img)
        #Clear the stream to get ready for next frame.    
        rawCapture.truncate(0)
        rawCapture.seek(0)
        if sampleNum>40:
            break
        
        if key==ord("q"):
            break
        #Give the imshow some time to refresh
        cv2.waitKey(1)
    cv2.destroyAllWindows()

#Functions needed for training
def getImages(path, subDirs):
    faces = []
    IDs = []
    for subDir in subDirs:
        path = subDir
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
        ''' This will concatenate the root path with the imagename thus creating a list with all image paths.
         f = imagename ---> concatenate (path,f)'''
        '''Now we will loop over the images and extract the faces and IDs'''
        for imagePath in imagePaths:
            faceImg = Image.open(imagePath).convert('L'); ''' Open image and convert it to greyscale. This results in a PIL (Python Image Library) image, but we need a NumPy array to work with it'''
            faceNp = np.array(faceImg)
        
        
    #        # print (faceNp.shape) #This prints the dimensions of the images; note that the images have different dimensions
    #               
            IDtemp = os.path.split(imagePath)[-1]# ''' Use path splitter and then split after first dot. [-1] will give the last element of the path: /User.1.1.jpg. [1] will give the userID which is the element after the first dot'''
            #print (IDtemp)
            ID = int(IDtemp.split('.')[1])

            # The train function needs integers instead of strings for its algorithm. We will convert the names to their corresponding integer values.
            #print (ID)
            #ID = int(ID1) ''' Convert string to integer '''

            faces.append(faceNp)
            IDs.append(ID)
            cv2.imshow("Training",faceNp)
            cv2.waitKey(100)
    return faces, np.array(IDs)


def training():
    path='DataSet' #All pictures are saved in dataSet file
    #subDirs = os.walk(path) #Will yield a tuple for each subdirectory. The first entry in the 3-tuple is a directory name so:
    subDirs = [x[0] for x in os.walk(path)]
    subDirs = subDirs[1:len(subDirs)] #First entry will be the root directory, which only contains the subfolders for each person.

    faces, IDs = getImages(path, subDirs)
    #print('IDs are: '+str(IDs))
    #Train using OpenCV
    recognizer.train(faces,IDs)
    # Write a yml file that is used to detect.
    recognizer.write('recognizer/trainingData.yml')
    cv2.destroyAllWindows()
    
    
    
def contRecognition(self= None):
    global interrupt
    global running
    global cF
    interrupt=False
    running= True

    unknownCounter = 0
    newMail = True
    sendTime = time.time()
    
    #Initializing camera and grab a reference to the raw camera capture
    #camera=PiCamera()
    global camera
    #Adjusting some properties
    camera.resolution=(640,480)
    camera.framerate=FPS
    #This function creates a 3D RGB-array from a RGB capture
    rawCapture=PiRGBArray(camera)
    
    recognizer.read('/home/pi/Documents/Facial recog/recognizer/trainingData.yml')

    #Create scheduling Thread. This will check every 5 minutes if unkownCounter>5 and if so , send an email

    #global mailFlag #Global flag for sending mail

    #Starting scheduler thread (I don't know if it is necessary to do it with thread or if we can do it without, but I couldn't check it)
    #t = threading.Thread(target=mailSched())
    #t.daemon = True
    #t.start()

    #Capture frames from camera
    for frame in camera.capture_continuous(rawCapture,format='bgr'):
        #Grab NumPy array from image
        img=frame.array
        #Show the unprocessed frame
        #cv2.imshow("Imag",img)
        key=cv2.waitKey(1)&0xFF

        #Convert RGB to grayscale
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces= detector.detectMultiScale(gray,1.3,5)

        #Send mail if new person is detected. This code is placed here so there is no text/rectangles on the image
        '''if (unknownCounter > 5 and newMail):
            cv2.imwrite('/home/pi/Documents/Facial recog/mailImg.jpg',img)
            sendMail()
            newMail = False'''

        
        t2 = time.time()
        if (unknownCounter == 5 and newMail) :
            cv2.imwrite('/home/pi/Documents/Facial recog/mailImg.jpg',img)
            #sendMail('mailImg.jpg') #Commented because you have to enter username and password manually in code
            t1 = time.time()
            newMail = False
        elif (not(newMail) and (t2-t1 > 300)):
            unknownCounter = 0
            newMail = True
        else:
            None

            
        #Draw a rectangle around every face and add Id
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            ID, conf = recognizer.predict(gray[y:y+h,x:x+w])

            userName = findName(ID)
                
            #If difference between database and picture is small enough--> recognize
            if (conf<65):
                cv2.putText(img,str(userName),(x,y+h),font,4,(255,0,0),2,cv2.LINE_AA);
            else: 
                cv2.putText(img,"Unknown",(x,y+h),font,4,(255,0,0),2,cv2.LINE_AA);
                userName = 'Unknown'


            #If you find an unknown person for at least 5 frames: send an email with the unknown face
            #This should not occur more than once every 5 min?
            if (userName == "Unknown"):
                unknownCounter += 1
            else:
                unknownCounter = 0

            
            #Add text to pic (the name of whom that is recognized)
            #cF.frame=img
            #cF.name=userName
            #cF.cert=conf
            #if self is not None:
                #self.label_bot.config(text=('Name = ' + str(userName)))
                #self.label_bot2.config(text=('Certainty = ' + str(conf)))
            #cv2.putText(img,'Certainty: '+str(conf),(0,40),font,4,(0,0,255),2,cv2.LINE_AA)
            print('Certainty:'+ str(conf))    
        cv2.imshow('frame', img)
        #Clear the stream to get ready for next frame. 
        rawCapture.truncate(0)
        rawCapture.seek(0)

        #If you keep pressing q loop ends.
        if interrupt:
            print('Exiting continuous recognition')
            break
        elif not running:
            print('Exiting continuous recognition')
            break
        #Give the imshow some time to refresh
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    

#Functions needed for continuous recognition
def findName(ID):
    userName = 'Unknown'
    try:
        f = open('mapping.txt','r')
    except:
        print('File not found')
        return userName
    for line in f:
        userID = int(line.split('.')[1])
        if (ID == userID):
            userName = line.split('.')[0]
            break
        else:
            userName = 'Unknown'
    f.close()
    return userName

print_lock=threading.Lock()

def inputScanner():
    global interrupt
    global running
    #with print_lock:
    while True:
        command=str(input("Type R to return to menu and Q to quit.-->"))
            
        command=command.upper()
        print(command)
        if command =='R':
            print('Interrupting')
            interrupt = True
        elif command == 'Q':
            print('Quitting')
            running = False
        else:
            print('Command not recognized.')
                

def createThread():
    q=Queue()
    t=threading.Thread(target=inputScanner)
    t.daemon = True
    t.start()
    return t

    
def Main():
    global running
    '''
    #Initializing camera and grab a reference to the raw camera capture
    camera=PiCamera()
    #Adjusting some properties
    camera.resolution=(640,480)
    camera.framerate=30
    #This function creates a 3D RGB-array from a RGB capture
    rawCapture=PiRGBArray(camera)
    #Allow camera to initialize. Not really necessary but can't hurt.
    time.sleep(0.1)
    '''
    
    createThread()
    while running:
        contRecognition()
        #with print_lock:
        if True:
            if running == False:
                break
            choice = makeChoice()
            if (choice == 1):
                print("Recognizing new face")
                newRecognition()
            elif (choice == 2):
                print("Training")
                training()
            elif (choice == 3):
                print("Continuous recognition")
                createThread()
                contRecognition()
                
            else:
                print("Invalid input")
                choice = makeChoice()
    

            
    print("Terminating program")
    
def sendMail(mailImg):
    print('Mail will be sent')
    
    ''' Initialization '''
    sender = "<Sender email>"
    senderPW = "<Sender password>"               # Unencrypted password. Should probably be changed somehow.
    receiver = "<Receiver email>"
    msg = MIMEMultipart()
    msg['Subject'] = "Unknown person detected"
    msg['From'] = sender
    msg['To'] = receiver
    ''' Build email '''
    # Create MIME multipart message (multipart message is needed in case we want to attach text messages, images,... NonMultipart messages seem useless)
       
    # Attach the body of the email to the MIME message
    body = MIMEText("An unknown person was detected by the Raspberry Pi security system. His or her photo is attached in this mail", 'plain')
    msg.attach(body)
    # Attach image to the MIME message
    img_data = open(mailImg, 'rb').read()
    image = MIMEImage(_imagedata=img_data, name=os.path.basename('Stranger.png'))
    msg.attach(image)


    ''' SMTP '''
    server = smtplib.SMTP('smtp.gmail.com', 587) #587 is TLS port, 465 is SSL port (older version of TLS)
    #Put the SMTP connection in TLS (Transport Layer Security) mode. All SMTP commands that follow will be encrypted. You should then call ehlo() again.
    #EHLO (or HELO) identifies the server initiating the connection
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender, senderPW)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()
   
if __name__=="__main__":
    Main()
