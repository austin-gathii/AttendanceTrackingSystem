import time
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import cv2,facialRecognition,threading,auxFunctions,json
from PIL import Image,ImageTk
import matplotlib.pyplot as plt
from datetime import datetime
from auxFunctions import *
import numpy as np
#CONSTANTS
SYS_STATE = {1:0,2:0,3:0,4:0}
#0 .. no face found, inactive
#1 .. face found attempting recognition
#2 .. face found cannot be recognized
#3 .. registering new face

def updateSysState(flag,val):
    global SYS_STATE
    if SYS_STATE[flag] == 0:
        SYS_STATE[flag] += val

def getSysState(ghost = False):
    global SYS_STATE
    for key,val in reversed(SYS_STATE.items()):
        if val > 0:
            if not ghost:
                SYS_STATE[key] -= 1
            return key
    return 0





class mainWindow(tk.Tk):
    def __init__(self):
        #MAIN WINDOW DEFINITIONS
        super().__init__()
        self.title("ATTENDANCE TRACKING SYSTEM")
        winLeft = str((self.winfo_screenwidth() - 700) // 2)
        winTop = str((self.winfo_screenheight() - 700) // 2 - 20)
        self.geometry("700x700+" + winLeft + "+" + winTop)
        self.resizable(False, False)

        #MAIN FRAME
        self.mainFrame = ttk.Frame(self, width=675, height=675)
        self.mainFrame["padding"] = 10

        #self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.columnconfigure(1, weight=1)

        #self.mainFrame.rowconfigure(0, weight=3)
        self.mainFrame.rowconfigure(1, weight=1)
        self.mainFrame.pack(fill="both", expand=True)


        #STYLES
        self.style = ttk.Style(self)
        self.style.configure("TLabel", background="black", foreground="white")
        self.style.configure("TFrame", background="black", foreground="white")
        self.style.configure("TButton",background="white", foreground="black", font=("Century Gothic", 12))


        self.style.configure("attRecording.TFrame",hightlightbackground = "white",highlightthickness = "5")


        self.style.configure("registerUser.TLabel", background="black", foreground="white", font=("Century Gothic", 12, "underline"))
        self.style.configure("timeLabel.TLabel", background="black", foreground="white", font=("Century Gothic", 12, "underline"),
                        padding=15)
        self.style.configure("actualTime.TLabel", background="black", foreground="white", font=("Century Gothic", 25),
                        padding=0)
        self.style.configure("attRecording.TLabel", background="black", foreground="white", font=("Century Gothic", 12),
                             padding=0)
        self.style.configure("faceDetectedLabel.TLabel", foreground="white", font=("Century Gothic", 12), padding=20)
        self.style.configure("noFaceDetectedLabel.TLabel", foreground="red", font=("Century Gothic", 15), padding=20)

        #INIT ALL MODULES
        self.camView = CamView(self)
        self.infoShelf = InfoShelf(self)
        self.dataStream = DataStream(self)


class CamView(ttk.Label):
    def __init__(self,root):
        super().__init__(root.mainFrame)
        self.grid(column=0, row=0, sticky=tk.NW)
        self.cap = cv2.VideoCapture(0)
        self.userData = auxFunctions.getTableData("Employees")
        self.embBuffer = []

        #cam view vars
        self.frameSize = 175
        self.frameCols = {0:(100,100,100),1:(150,150,250),2:(250,150,150),3:(150,250,150),4:(250,175,100)}
        #.....
        self.perfRecognitionFlag = False
        self.perfRegistrationFlag = False
        self.embThread = None
        self.myEmbedding = None
        self.currEmb = None
        self.thisPerson = None
        self.regUser = None
        self.faceSearchDuration = 0
        self.showWebcamView()




    def showWebcamView(self):
        rawImg = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB)
        imgDim = min(rawImg.shape[:2])
        rawImg = rawImg[int(rawImg.shape[0] / 2 - imgDim / 2):int(rawImg.shape[1] / 2 + imgDim / 2),
                 int(rawImg.shape[0] / 2 - imgDim / 2):int(rawImg.shape[1] / 2 + imgDim / 2)]


        # Applying the face detection method on the grayscale image
        #faces_rect = haar_cascade.detectMultiScale(cv2.cvtColor(rawImg, cv2.COLOR_RGB2GRAY), 1.1, 9)
        face_rects,prob = facialRecognition.mtcnn.detect(rawImg)
        faces = facialRecognition.mtcnn(rawImg)
        face_rects = face_rects if isinstance(face_rects,np.ndarray) else []


        # get the largest rect
        if len(face_rects) > 0:
            faceIdx,faceRect = max(list(enumerate(face_rects)), key=lambda x: (x[1][2] - x[1][0]) * (x[1][3] - x[1][1]))
            if prob[faceIdx] > 0.8 and 250-50 < (faceRect[2]+faceRect[0])/2 < 250+50 and 250-50 < (faceRect[3]+faceRect[1])/2 < 250+50:
                updateSysState(1, 1)
                if getSysState(True) == 1:
                    self.perfRecognitionFlag = True

        else:
            faceRect = None


        #getting the embeddings
        if (self.embThread == None or not self.embThread.is_alive()) and faces != None:
            self.embBuffer = self.embBuffer[-50:]
            self.embThread = threading.Thread(
                target=lambda: self.embBuffer.append(facialRecognition.getFaceEmbedding(faces[0])))
            self.embThread.start()


        if not isinstance(faceRect,np.ndarray) and self.perfRegistrationFlag and self.regUser != None:
            updateSysState(4,1)
            self.performRegistration()


        elif len(face_rects) > 0 and self.perfRecognitionFlag:
            self.performRecognition()
            if not isinstance(self.thisPerson,dict):
                self.faceSearchDuration+=1
                if self.faceSearchDuration > 100:
                    updateSysState(2,5)
                    print("This face is not recognized, you should probably click add user to register...")
                    self.faceSearchDuration = 0
                    self.perfRecognitionFlag = False

            else:
                self.faceSearchDuration = 0
                self.perfRecognitionFlag = False
                updateSysState(3, 10)
                print("Found you ", self.thisPerson["firstName"])




        if getSysState(True) != 3:
            self.thisPerson = None
            pass





        img = cv2.resize(rawImg, (500, 500))
        #drawing the camera view overlays
        #main frame
        for cnr in [(10,10),(490,10),(10,490),(490,490)]:
            cv2.line(img,cnr,(cnr[0]+(80 if cnr[0] < 250 else -80),cnr[1]),(0,0,0),4,cv2.LINE_AA)
            cv2.line(img,cnr,(cnr[0],cnr[1]+(80 if cnr[1] < 250 else -80)),(0,0,0),4,cv2.LINE_AA)

        #face border
        for cnr in [(250-self.frameSize//2,250-self.frameSize//2),(250+self.frameSize//2,250-self.frameSize//2),
                    (250-self.frameSize//2,250+self.frameSize//2),(250+self.frameSize//2,250+self.frameSize//2)]:
            cv2.line(img,cnr,(cnr[0]+(self.frameSize//5 if cnr[0] < 250 else -self.frameSize//5),cnr[1]),self.frameCols[getSysState(True)],3,cv2.LINE_AA)
            cv2.line(img,cnr,(cnr[0],cnr[1]+(self.frameSize//5 if cnr[1] < 250 else -self.frameSize//5)),self.frameCols[getSysState(True)],3,cv2.LINE_AA)

        #search indicator
        for arc in range(0,360,90):
            offset = 360*(time.time()%5)/5
            arc = int((arc+offset)%360)
            cv2.ellipse(img,(250,250),(140,140),0,arc,arc+30,self.frameCols[getSysState(True)],3)




        imgtk = ImageTk.PhotoImage(Image.fromarray(img))
        self.imgtk = imgtk
        self.configure(image=imgtk)

        self.after(20, self.showWebcamView)


    def performRecognition(self):
        if len(self.embBuffer) > 0:
            #self.embBuffer = self.embBuffer[-10:]
            self.currEmb = self.embBuffer[-1]
            fits = sorted([[user,self.compareFaces(self.currEmb,json.loads(user["facialData"]))] for user in self.userData.values() if user["facialData"] != None],key = lambda x:self.compareFaces(self.currEmb,json.loads(x[0]["facialData"])))
            if len(fits) > 0:
                bestFit = fits[0]
                #print(bestFit[1])
                if bestFit[1] < 0.35:
                    prevAttendance = auxFunctions.getAttendanceData()
                    maxTime = None
                    for stamp in prevAttendance:
                        if stamp["userId"] == bestFit[0]["Id"]:
                            rTime = datetime.strptime(stamp["timestamp"], "%Y-%m-%d %H:%M:%S").timestamp()
                            if maxTime == None or rTime > maxTime:
                                maxTime = rTime

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    self.thisPerson = bestFit[0]

                    if maxTime == None or datetime.now().timestamp() - maxTime > 10*60:

                        auxFunctions.insertData("Attendance",{"userId":self.thisPerson["Id"],"timestamp":timestamp})


    def performRegistration(self):
        if len(self.embBuffer) > 20:
            self.regUser["facialData"] = json.dumps([x[0].tolist() for x in self.embBuffer[:50]])
            self.embBuffer = self.embBuffer[:10]
            auxFunctions.updateData("Employees",self.regUser["Id"],self.regUser)
            self.userData = auxFunctions.getTableData("Employees")
            self.regUser = None
            self.perfRegistrationFlag = False






    def compareFaces(self,newFace,faceList):
        diff = min([np.linalg.norm((newFace-np.array(f))) for f in faceList])
        return diff




class InfoShelf(ttk.Frame):
    def __init__(self,root):
        super().__init__(root.mainFrame,style = "infoShelf.TFrame")
        self.root = root
        self.grid(column=1, row=0, rowspan = 2, sticky=tk.NSEW)

        #TIME LABEL
        self.timeLabel = ttk.Label(self, text="TIME", style="timeLabel.TLabel", anchor=tk.CENTER)
        self.timeLabel.pack(fill="x", ipady=0)

        # CURRENT TIME
        self.actualTime = ttk.Label(self, style="actualTime.TLabel", anchor=tk.CENTER)
        self.actualTime.pack(fill="x", ipady=0)

        #ATTENDANCE LABEL
        self.attendanceLabel = ttk.Label(self, text="ATTENDANCE LIST", style="timeLabel.TLabel", anchor=tk.CENTER)
        self.attendanceLabel.pack(fill="x", ipady=10)


        #MULTIPURPOSE FRAME
        self.holderFrame = ttk.Frame(self,style = "Attendances.TFrame")
        self.holderFrame.pack(fill = "both",expand = True)

        #ATTENDANCES FRAME
        self.attendanceFrame = ttk.Frame(self.holderFrame, style="Attendances.TFrame",padding = (10,10))
        self.attendanceFrame.pack(fill = "x")
        self.allAttendances = []


        #ADD NEW USER FRAME
        self.addUserFrame = ttk.Frame(self.holderFrame)

        #User entries
        '''self.firstName = tk.StringVar()
        self.firstNameLabel = ttk.Label(self.addUserFrame,text = "First Name :")
        self.firstNameEntry = tk.Entry(self.addUserFrame,textvariable = self.firstName)

        self.lastName = tk.StringVar()
        self.lastNameLabel = ttk.Label(self.addUserFrame, text="Last Name :")
        self.lastNameEntry = tk.Entry(self.addUserFrame, textvariable=self.lastName)'''

        self.Id = tk.StringVar()
        self.idLabel = ttk.Label(self.addUserFrame, text="Employee Id :",style = "registerUser.TLabel")
        self.idEntry = tk.Entry(self.addUserFrame, textvariable=self.Id)

        self.Password = tk.StringVar()
        self.passwordLabel = ttk.Label(self.addUserFrame, text="Employee Password :",style = "registerUser.TLabel")
        self.passwordEntry = tk.Entry(self.addUserFrame, textvariable=self.Password,show = "*")

        self.registerUserButton = ttk.Button(self.addUserFrame,text = "REGISTER FACE")
        self.registerUserButton.bind("<Button>",lambda event:threading.Thread(target = self.onClickRegisterFace).start())

        #pack user entry widgets to frame
        #self.firstNameLabel.pack(fill = "x",pady = 2)
        #self.firstNameEntry.pack(fill = "x",ipady = 10,pady = 5)
        #self.lastNameLabel.pack(fill = "x",pady = 2)
        #self.lastNameEntry.pack(fill = "x",ipady = 10,pady = 5)
        self.idLabel.pack(fill = "x",pady = 2)
        self.idEntry.pack(fill = "x",ipady = 10,pady = 5)
        self.passwordLabel.pack(fill = "x",pady = 2)
        self.passwordEntry.pack(fill = "x",ipady = 10,pady = 5)
        self.registerUserButton.pack(fill = "x",ipady = 10,pady = 5)



        #NEW USER BUTTON
        self.addUserButton = ttk.Button(self,text = "ADD NEW USER")
        self.addUserButton.pack(ipady = 10,pady = 10,fill = "x")
        self.addUserButton.bind("<Button>",self.onClickAddUser)

        #UPDATE
        self.updateTimeAndAttendance()



    def updateTimeAndAttendance(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.actualTime.configure(text=current_time)

        myAttendances = auxFunctions.getAttendanceData()
        myAttendances = [mat for mat in myAttendances if datetime.strptime(mat["timestamp"], "%Y-%m-%d %H:%M:%S").date() == datetime.now().date()]
        if len(myAttendances) > len(self.allAttendances):
            allUsers = auxFunctions.getTableData("Employees")
            for allat in self.allAttendances:
                allat.pack_forget()
            self.allAttendances.clear()
            for mat in sorted(myAttendances,key = lambda x:x["attId"],reverse = True):
                recordFrame = tk.Frame(self.attendanceFrame,highlightbackground="white", highlightthickness=2,background = "black")
                ttk.Label(recordFrame,text=mat["timestamp"].split(" ")[1],style = "attRecording.TLabel").pack(fill = "x")
                ttk.Label(recordFrame,text = f"Id No.{mat['userId']}",style = "attRecording.TLabel").pack(fill = "x")
                ttk.Label(recordFrame,text = f"{allUsers[mat['userId']]['firstName']} {allUsers[mat['userId']]['lastName']}",style = "attRecording.TLabel").pack(fill = "x")
                recordFrame.pack(fill = "x",ipady = 10)
                self.allAttendances.append(recordFrame)




        self.actualTime.after(1000, self.updateTimeAndAttendance)

    def onClickAddUser(self,event):
        if event.widget["text"] == "ADD NEW USER":
            self.attendanceFrame.pack_forget()
            self.addUserFrame.pack(fill = "x")
            event.widget.configure(text = "CANCEL")
        else:
            self.addUserFrame.pack_forget()
            self.attendanceFrame.pack(fill="x")
            event.widget.configure(text="ADD NEW USER")

    def onClickRegisterFace(self):
        allEmployees = getTableData(MAIN_TABLE)
        if not any(x.get() == "" for x in [self.Id,self.Password]):
            iid = int(self.Id.get())
            if iid in allEmployees.keys():
                if allEmployees[iid]["Password"] == self.Password.get():
                    #ALL_EMPLOYEES[self.Id.get()]["FacialData"] = "Yeah, I know him" #This is where we input the facial data
                    self.root.camView.perfRegistrationFlag = True
                    self.root.camView.embBuffer = []
                    self.root.camView.regUser = allEmployees[iid]
                    self.Password.set("")
                    self.Id.set("")
                    while isinstance(self.root.camView.regUser,dict):
                        time.sleep(1)
                    mb.showinfo("Successfully registered",
                                f"Your face has been successfully registered to the "
                                f"system... as {allEmployees[iid]['firstName']}"
                                f" {allEmployees[iid]['lastName']}")
                    self.addUserFrame.pack_forget()
                    self.attendanceFrame.pack(fill="x")
                    self.addUserButton.configure(text="ADD NEW USER")
                else:
                    mb.showerror("Incorrect Password","That password is incorrect for the specified Employee Id")
            else:
                mb.showerror("Unknown Employee Id","The given Employee Id is not available in the system")
        else:
            mb.showerror("Missing information","Please fill in all entry fields")




class DataStream(ttk.Frame):
    def __init__(self,root):
        super().__init__(root.mainFrame,style = "infoShelf.TFrame")
        self.root = root
        self.grid(column=0, row=1, sticky=tk.NSEW)
        self.messages = ["No face detected,\n position your face within the center frame","Face Detected,\n undergoing facial recognition..",
                         "Unfortunately the face in view is unrecognized,\n try again..","Face has been recognized,\n Welcome",
                         "New face being registered,\n Please wait..."]
        self.faceDetectedLabel = ttk.Label(self,text = "Check if face",style = "faceDetectedLabel.TLabel")
        self.faceDetectedLabel.pack(fill = "both",expand = True)

        self.updateFaceDetection()



    def updateFaceDetection(self):
        sysState = getSysState()
        person = self.root.camView.thisPerson
        message = self.messages[sysState].upper()
        if person != None:
            message += (" "+person["firstName"]+" "+person["lastName"]).upper()
        self.faceDetectedLabel.configure(text=message)
        #self.faceDetectedLabel.configure(style = "faceDetectedLabel.TLabel")


        self.faceDetectedLabel.after(1000,self.updateFaceDetection)









if __name__ == '__main__':
    root = mainWindow()
    root.mainloop()

