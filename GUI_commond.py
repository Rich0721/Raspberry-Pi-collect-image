from tkinter import messagebox as msg
from PIL import ImageTk, Image
from tkinter import filedialog
import re
import json
import cv2
import os
from glob import glob
from picamera.array import PiRGBArray
from picamera import PiCamera
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

def CheckUserInput(stringVars:dict, alarmVars:list):

    check_pass = True

    if len(stringVars['Project_name'].get()) == 0 or len(stringVars["FTP_IP"].get()) == 0 or\
            len(stringVars["user"].get()) == 0 or len(stringVars["password"].get()) == 0:
        check_pass = False

    time_text = ""
    ftp_ip = stringVars['FTP_IP'].get()
    if not re.search(IP_RELU, ftp_ip):
        alarmVars[0].set("OA's IP is 10.96.X.X, FAB's IP is 10.97.X.X")
    else:
        if not Test_FTP(ftp_ip, stringVars['user'].get(), stringVars['password'].get()):
            alarmVars[0].set("FTP IP, user or password are error!")
            check_pass = False
        else:
            alarmVars[0].set("")

    if str.isdigit(stringVars['sensor'].get()):
        if int(stringVars['sensor'].get()) not in PI_USED_PIN:
            alarmVars[1].set("Pleaser study GPIO's documation!")
            check_pass = False
    elif  len(stringVars['sensor'].get()) == 0:
        pass
    else:
        if not str.isdigit(stringVars['sensor'].get()):
            alarmVars[1].set("IR sensor only key in digit!")
            check_pass = False
    
    if str.isdigit(stringVars['video_time'].get()) or len(stringVars['video_time'].get()) == 0:
        pass
    else:
        time_text += "Video time must is digit!"
        check_pass = False
    
    if str.isdigit(stringVars['interval_time'].get()) or len(stringVars['interval_time'].get()) == 0:
        pass
    else:
        time_text += " delay time must is digit!"
        check_pass = False
    
    if len(time_text) > 0:
        alarmVars[2].set(time_text)
    
    if check_pass:
        show_text = "Please check the following information\nProject Name:{}\nFTP IP:{}\nUser:{}\nPassword:{}\n".format(stringVars['Project_name'].get(), ftp_ip, stringVars["user"].get(), stringVars['password'].get())
        if stringVars["method"].get() == 0:
            show_text += "Method:Image\n"
        elif stringVars["method"].get() == 1:
            show_text += "Method:Video\n"

        if len(stringVars['path'].get()) > 0:
            show_text += "Path:{}\n".format(stringVars['path'].get())
        
        if len(stringVars['sensor'].get()) > 0:
            show_text += "Sensor PIN:{}\n".format(stringVars['sensor'].get())
        
        if len(stringVars['video_time'].get()) > 0:
            show_text += "Video time:{}\n".format(stringVars['video_time'].get())
        
        if len(stringVars['interval_time'].get()) > 0:
            show_text += "Delay time:{}".format(stringVars['interval_time'].get())

        MsgBox = msg.askyesno("Created Check", show_text)
        if MsgBox:
            write_json(stringVars['Project_name'].get() + ".json", stringVars)
    else:
        msg.showerror("Create error", "Please check data.")
        

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

    if len(stringVars["path"].get()) == 0:
        data["Used_condition"] = False
    else:
        data["Used_condition"] = True
        data["Condition_path"] = stringVars["path"].get()
    
    if len(stringVars["sensor"].get()) == 0:
        data["sensor"] = False
    else:
        data["sensor"] = True
        data["pin"] = int(stringVars["sensor"].get())
    
    if data['method'] == "video":
        if len(stringVars["video_time"].get()) == 0:
            data["video_time"] = 60
        else:
            data["video_time"] = int(stringVars["video_time"].get())
    
    if len(stringVars["interval_time"].get()) == 0:
        data["delay"] = 0
    else:
         data["delay"] = int(stringVars["interval_time"].get())
        
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


def savePhoto(path, frame):
    if frame is not None:
        images = glob(os.path.join("./condition_images", "condition_*.jpg"))
        path = os.path.join("./condition_images", "condition_" + str(len(images)) + ".jpg")
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join("./condition_images", "condition_" + str(len(images)) + ".jpg"), frame)


# Select image's roi and save result.
def cutPhoto(path, roi, frame):
    if frame is not None:
        
        # save image
        images = glob(os.path.join("./condition_images", "condition_*.jpg"))
        path = os.path.join("./condition_images", "condition_" + str(len(images)) + ".jpg")
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join("./condition_images", "condition_" + str(len(images)) + ".jpg"), frame)

        original_h, original_w = frame.shape[:2]
        display_h = 480
        display_w = 640
        rate_w = original_w / 640
        rate_h = original_h / 480
        draw = drawRoI(rate_w, rate_h)
        img = cv2.resize(frame, (display_h, display_w))
        draw.call(img)
        while True:
            cv2.imshow("Cut Image", draw.show_image())
            key = cv2.waitKey(1)
            
            # Close program with keyboard 'q'
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
        roi.append(draw.get_rectangle())


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