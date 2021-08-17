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


def savePhoto(path, roi, frame):
    if frame is not None:
        images = glob(os.path.join("./condition_images", "condition_*.jpg"))
        path.append(os.path.join("./condition_images", str(len(images) + ".jpg")))
        roi.append([])
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join("./condition_images", str(len(images) + ".jpg")), frame)


# Select image's roi and save result.
def cutPhoto(path, roi, frame):
    if frame is not None:
        images = glob(os.path.join("./condition_images", "condition_*.jpg"))
        path.append(os.path.join("./condition_images", str(len(images) + ".jpg")))
        frame = cv2.cvtColor(frame)
        cv2.imwrite(os.path.join("./condition_images", str(len(images) + ".jpg")), frame)

        original_h, original_w = frame.shape[:2]
        display_h = 480
        display_w = 640
        img = cv2.resize(frame, (display_w, display_h))
        rects = []
        while True:
            cv2.imshow("image", img)
            rect = cv2.selectROI("image", img, showCrosshair, fromCenter)
            (x, y, w, h) = rect
            img = cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1)

            x = x * (original_w / 640)
            y = y * (original_h / 480)
            w = w * (original_w / 640)
            h = h * (original_h / 480)

            rects.append([int(x), int(y), int(w), int(h)])

            cv2.destroyAllWindows()
            key = cv2.waitKey(0) & 0xFF

            if key == ord('q'):
                break

        roi.append(rects)