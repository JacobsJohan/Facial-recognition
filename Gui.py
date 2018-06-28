from tkinter import *
import FullRecognition as fr
import threading

WIDTH = 720
HEIGHT = 480
counter = 0

cF = fr.currentFrame()

# -------MAINMENU-------
class MainMenu:
    def __init__(self,master):
        self.root = master
        self.bottomFrame = Frame(master)
        self.button_1 = Button(self.bottomFrame, text="Learn New Face", command=lambda: changeView(self, 'nf'))
        self.button_1.grid(row=1, column=0,  padx=10, pady=20)
        self.button_2 = Button(self.bottomFrame, text="Training", command=lambda: changeView(self, 't'))
        self.button_2.grid(row=1, column=1, padx=10, pady=20)
        self.button_2 = Button(self.bottomFrame, text="Continuous Recognition", command=lambda: changeView(self, 'cr'))
        self.button_2.grid(row=1, column=2, padx=10, pady=20)
        self.bottomFrame.grid(row=1, column=0)

        self.upperFrame = Frame(master)
        self.label_1 = Label(self.upperFrame, text='Welcome to our facial recognizer')
        self.label_1.grid(padx= WIDTH/3+17, pady=50, columnspan=5)
        self.upperFrame.grid(row=0, column=0)

        self.frames = []
        self.frames.append(self.upperFrame)
        self.frames.append(self.bottomFrame)

        root.geometry('{}x{}'.format(WIDTH,HEIGHT))


def changeView(self, kindOfSwitch):
    destroyFrames(self.frames)
    kindOfSwitch=kindOfSwitch.lower()
    if kindOfSwitch == "nf":
        newFace(self.root)
    elif kindOfSwitch == "t":
        print()
        trainerScreen(self.root)
    elif kindOfSwitch == "cr":
        contRecog(self.root)
    else:
        print("Internal error")


# ---------Cont recog window-----------
class contRecog:
    global cF
    def __init__(self,master):
        #self.photo = PhotoImage(file='test.png')

        self.upperFrame = Frame(master)
        self.button_1 = Button(self.upperFrame, text="Start", command=self.startRecog)
        #self.button_1.bind("<Button-3>", self.printName3)
        self.button_1.grid(padx=WIDTH/2-35, pady=10)
        self.button_2 = Button(self.upperFrame, text="Pause", command=self.breakFr)
        #self.button_2.bind("<Button-3>", self.printName)
        self.button_2.grid(padx=WIDTH/2-35, pady=10)
        self.button_3 = Button(self.upperFrame, text="Return", command=lambda: returnToMenu(self))
       #self.button_3.bind("<Button-3>", self.printName)
        self.button_3.grid(padx=WIDTH/2-35, pady=10)
        self.upperFrame.grid(row=0, column=1)


##        self.leftFrame = Frame(master)
##        self.label_img = Label(self.leftFrame, image=self.photo)
##        self.label_img.pack()
##        self.leftFrame.grid(row=0, column=0)

        '''self.bottomFrame=Frame(master)
        self.label_bot=Label(self.bottomFrame, text=('Name = ' + str(cF.name)))
        self.label_bot2=Label(self.bottomFrame, text=('Certainty = ' + str(cF.cert)))
        self.label_bot.grid(row=0, column=0, padx=50)
        self.label_bot2.grid(row=0, column=1, padx=50)
        self.bottomFrame.grid(row=3)'''

        self.frames=[]
        self.frames.append(self.upperFrame)
        #self.frames.append(self.leftFrame)
        #self.frames.append(self.bottomFrame)


    '''def changeFrame(self): #add frame as input
        while fr.running:
            #self.label_img.config(image=fr.cF.frame) #For the moment the frame for opencv is an RGB array and tkinter can't work with this so we'll need to create a converter.
            self.label_bot.config(text=('Name = ' + str(fr.cF.name)))
            self.label_bot2.config(text=('Certainty = ' + str(fr.cF.cert)))
            if fr.interrupt:
                break
            time.sleep(1/fr.FPS)'''

            

    def startRecog(self):
        print('Starting cont recog')
        t=threading.Thread(target=fr.contRecognition, args=(self,))
        t.daemon=True
        t.start()
        

    def breakFr(self):
        print('Interrupting')
        fr.interrupt=True
        fr.running= False
        print(fr.interrupt)
        print(fr.running)

# -----------New face window-----------
#Here we have to make adjustments comparable to the ones in the contrecog
class newFace:
    def __init__(self,master):
        self.name=None

        #self.photo = PhotoImage(file='test.png')
        self.root=master

        self.upperFrame = Frame(master)
        #self.label_1 = Label(self.upperFrame, text='Enter nr of Pictures to take:')
        #self.label_1.grid()
        #self.entryName= Entry(self.upperFrame)
        #self.entryName.grid(row=1, column=0)
        self.button_1 = Button(self.upperFrame, text="Start", command=self.startLearning)
        self.button_1.grid(padx=WIDTH/2-35, pady=10)
        self.button_2 = Button(self.upperFrame, text="Train", command=lambda: changeView(self,'t'))
        self.button_2.grid(padx=WIDTH/2-35, pady=10)
        self.button_3 = Button(self.upperFrame, text="Return", command=lambda: returnToMenu(self))
        self.button_3.grid(padx=WIDTH/2-35, pady=10)
        self.upperFrame.grid(row=0, column=0)

##        self.leftFrame = Frame(master)
##        self.label_img = Label(self.leftFrame, image=self.photo)
##        self.label_img.pack()
##        self.leftFrame.grid(row=0, column=0)

        self.frames=[]
        self.frames.append(self.upperFrame)
        #self.frames.append(self.leftFrame)


    def changeFrame(self): #add frame as input
        self.photo = PhotoImage(file='test2.png')
        self.label_img.config(image=self.photo)


    def startLearning(self):
        self.popUpMsg()
        if self.name == "":
            self.startLearning()    
        else:
            True
            fr.newRecognition(self.name)

    def popUpMsg(self):
        popup = Tk()

        def leavePopUp():
            self.name=entryName.get()
            popup.destroy()
            popup.quit()

        popup.wm_title("New face")
        label = Label(popup, text="Enter name:")
        label.pack(side="top", fill="x", pady=10)
        entryName = Entry(popup)
        entryName.pack()        
        b1 = Button(popup, text="Start", command=leavePopUp)
        b1.pack(side="right")
        b2 = Button(popup, text="Stop", command=popup.destroy)
        b2.pack(side="left")
        popup.mainloop()

# -----------Trainer window-----------
class trainerScreen:
    def __init__(self,master):

        self.upperFrame = Frame(master)
        self.progresslabel=Label(self.upperFrame, text=('Waiting for training to start'))
        self.progresslabel.grid()
        self.button_1 = Button(self.upperFrame, text="Start", command = self.startTraining)
        self.button_1.grid(row =1, padx=WIDTH/2-35, pady=10)
        self.button_4 = Button(self.upperFrame, text="Return", command = lambda: returnToMenu(self))
        self.button_4.grid(row=2, columnspan=3, padx=10, pady=10)
        self.upperFrame.grid(row=1, column=0)

        self.frames = []
        self.frames.append(self.upperFrame)
        #self.frames.append(self.leftFrame)

    #For the trainer we should use the step function every picture that is trained and take step= total width/nrofpicture

    def startTraining(self):
        self.progresslabel.config(text="Training in progress... \n Please wait until it is done.")
        fr.training()
        self.progresslabel.config(text='Training Done!')

# ---------Main functioning-----------
def Main():
    #Initialize tkinter
    root.resizable(width=False,height=False)

    #Create welcomeScreen
    MainMenu(root)
    
    #Create a frameinstance that keeps track of current frame,name and conf

    #Create general Menu
    menu = Menu(root)
    root.config(menu=menu)

    subMenu=Menu(menu)
    menu.add_cascade(label='Main', menu=subMenu)
    #menu.add_command(label='?', command=)
    #subMenu.add_separator()
    subMenu.add_command(label='Quit', command=Exit)

    infoMenu=Menu(menu)
    menu.add_cascade(label='Info', menu=infoMenu)
    infoMenu.add_command(label='About', command= printInfo)
def Exit():
    root.destroy()
    root.quit()

def printInfo():
    popup = Tk()

    def leavePopUp():
        popup.destroy()
    popup.wm_title("About")
    label = Label(popup, text="Facial recognition.\n Developped by Johan Jacobs and Giuseppe Van Campenhout at VUB.\n Under supervision of Evi Van Nechel and Cedric Busschots ")
    label.pack(side="top", fill="x", pady=10)
    b1 = Button(popup, text="OK", command =leavePopUp)
    b1.pack()
    popup.mainloop()


    #This function is needed to keep GUI displayed
    root.mainloop()


def returnToMenu(current):
    global root
    destroyFrames(current.frames)
    MainMenu(root)

def destroyFrames(frames):
    for frame in frames:
        frame.destroy()


if __name__=="__main__":
    root = Tk()
    #root.geometry("550x200")
    Main()
