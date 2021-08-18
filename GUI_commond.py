from tkinter import messagebox as msg
import re
import json
import cv2
#from picamera.array import PiRGBArray
#from picamera import PiCamera
from time import sleep
from ftplib import FTP

#################################################
IP_RELU = "^10.(96|97).+((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.)(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
PI_USED_PIN = [3, 5, 7, 8, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, \
                32, 33, 35, 36, 37, 38, 40]
showCrosshair = False # Don't display grid
fromCenter = False # Select top-left to button-right
#################################################

def limitInputDigital(P):
    if str.isdigit(P) or P == '':
        return True
    else:
        return False

def CheckUserInput(stringVars:dict):

    check_pass = True

    if len(stringVars['Project_name'].get()) == 0 or len(stringVars["FTP_IP"].get()) == 0 or\
            len(stringVars["user"].get()) == 0 or len(stringVars["password"].get()) == 0:
        check_pass = False
    
    ftp_ip = stringVars['FTP_IP'].get()
    if not re.search(IP_RELU, ftp_ip):
       msg.showwarning("Input error", "The FTP IP isn't OA or FAB.")
    #else:
    #    if not Test_FTP(ftp_ip, stringVars['user'].get(), stringVars['password'].get()):
    #        alarmVars[0].set("FTP IP, user or password are error!")
    #        check_pass = False
    #    else:
    #        alarmVars[0].set("")
    
    # 0 is hardware, 1 is software
    if stringVars["condition"].get() == 0:
        if stringVars['sensor'].get() == "Choose Sensor Pin":
            msg.showerror("Input error", "Sensor Pin must set!")
            check_pass = False
    elif stringVars["condition"].get() == 0:
        if stringVars['path'] is None:
            msg.showerror("Input error", "Must save or cut image")
            check_pass = False
            
    if str.isdigit(stringVars['video_time'].get()) or len(stringVars['video_time'].get()) == 0:
        pass
    else:
        msg.showerror("Input error", "Video time must is digit!")
        check_pass = False
    
    if str.isdigit(stringVars['interval_time'].get()) or len(stringVars['interval_time'].get()) == 0:
        pass
    else:
        msg.showerror("Input error", "Interval time must is digit!")
        check_pass = False
    
    if str.isdigit(stringVars['delay_time'].get()) or len(stringVars['delay_time'].get()) == 0:
        pass
    else:
        msg.showerror("Input error", "Delay time must is digit!")
        check_pass = False
    
    
    if check_pass:
        show_text = "Please check the following information\nProject Name:{}\nFTP IP:{}\nUser:{}\nPassword:{}\n".format(stringVars['Project_name'].get(), ftp_ip, stringVars["user"].get(), stringVars['password'].get())
        if stringVars["method"].get() == 0:
            show_text += "Method:Image\n"
        elif stringVars["method"].get() == 1:
            show_text += "Method:Video\n"

        if stringVars['path'] is not None:
            show_text += "Path:{}\n".format(stringVars['path'])
        
        if stringVars['roi'] is not None:
            show_text += "ROI: Use {} roi".format(len(stringVars['roi']))
        
        if stringVars['sensor'].get() != "Choose Sensor Pin":
            show_text += "Sensor PIN:{}\n".format(stringVars['sensor'].get())
        
        if len(stringVars['video_time'].get()) > 0:
            show_text += "Video time:{}\n".format(stringVars['video_time'].get())
        
        if len(stringVars['interval_time'].get()) > 0:
            show_text += "Interval time:{}".format(stringVars['interval_time'].get())
        
        if len(stringVars['delay_time'].get()) > 0:
            show_text += "Delay time:{}".format(stringVars['delay_time'].get())

        MsgBox = msg.askyesno("Created Check", show_text)
        if MsgBox:
            write_json(stringVars['Project_name'].get() + ".json", stringVars)
        

def write_json(file_name, stringVars:dict):

    data = {}
    data["project name"] = stringVars['Project_name'].get()
    data["FTP"] = stringVars['FTP_IP'].get()
    data["user"] = stringVars['user'].get()
    data["password"] = stringVars["password"].get()

    if stringVars["method"].get() == 0:
        data["method"] = "image"
    elif stringVars["method"].get() == 1:
        data["method"] = "video"
    
    if stringVars["condition"].get() == 0:
        data["trigger"] = "hardware"
        data["sensor"] = stringVars["sensor"].get()
    elif stringVars["condition"].get() == 1:
        data["trigger"] = "software"
        data["path"] = stringVars["path"]
        if stringVars["roi"] is None:
            data["Used_roi"] = False
        else:
            data["Used_roi"] = True
            data["roi"] = stringVars["roi"]
    
    if data['method'] == "video":
        if len(stringVars["video_time"].get()) == 0:
            data["video_time"] = 60
        else:
            data["video_time"] = int(stringVars["video_time"].get())
    
    if len(stringVars["interval_time"].get()) == 0:
        data["interval"] = 0
    else:
         data["interval"] = int(stringVars["interval_time"].get())
    
    if len(stringVars["delay_time"].get()) == 0:
        data["delay"] = 0
    else:
         data["delay"] = int(stringVars["delay_time"].get())
        
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def Test_FTP(ip, user, password):

    try:
        ftp = FTP()
        ftp.connect(ip, 21)
        ftp.login(user, password)
        ftp.quit()
        return True
    except:
        return False

class VideoCapture:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera)
        sleep(0.1)
        
    def get_frame(self):
        self.camera.capture(self.rawCapture, format='rgb')
        image =self.rawCapture.array
        self.rawCapture.truncate(0)
        return image 
    
    def __del__(self):
        self.camera.close()

class VideoCaptureWebCamera():
    
    def __init__(self):
        self.camers = cv2.VideoCapture(0)

    def get_frame(self):
        cap, frame = self.camers.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def __del__(self):
        self.camers.release()    

# Implement selectROI
class drawRoI:

    def __init__(self, rate_w, rate_h):

        self.drawing = False
        self.xmin = 0
        self.ymin = 0
        self.xmax = 0
        self.ymax = 0
        self.rects = []
        self.rate_w = rate_w
        self.rate_h = rate_h
    
    def draw(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.xmin = x
            self.ymin = y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.clone_image = self.temp_image.copy()
                cv2.rectangle(self.clone_image, (self.xmin, self.ymin), (x, y), (0, 0, 255), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            self.xmax = x
            self.ymax = y
            self.drawing = False
            self.temp_image = self.clone_image
            self.rects.append([int(self.xmin * self.rate_w), int(self.ymin * self.rate_h), int(self.xmax * self.rate_w), int(self.ymax * self.rate_h)])
        elif event == cv2.EVENT_RBUTTONDOWN:
            if len(self.rects) > 0:
                self.rects.pop()
                self.clone_image = self.original_image.copy()
                for rect in self.rects:
                    cv2.rectangle(self.clone_image, (int(rect[0]/self.rate_w), int(rect[1]/self.rate_h)), (int(rect[2]/self.rate_w), int(rect[3]/self.rate_h)), (0, 0, 255), 2)
                self.temp_image = self.clone_image
                
    def show_image(self):
        return self.clone_image

    def get_rectangle(self):
        if len(self.rects) == 0:
            raise ValueError("Need select ROI.")
        return self.rects

    def call(self, frame):
        self.original_image = frame
        self.temp_image = frame.copy()
        self.clone_image = self.original_image.copy()

        cv2.namedWindow("Cut Image")
        cv2.setMouseCallback("Cut Image", self.draw)