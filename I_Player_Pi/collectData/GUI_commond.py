from tkinter import messagebox as msg
import os
import re
import json
import cv2
from collectData.selectData import collectImageOrVideo
from time import sleep
from ftplib import FTP
from os.path import exists


#################################################
IP_RELU = "^10.(96|97).+((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.)(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
GPIO_PIN = {'3':2, '5':3, '7':4, '11':17, '13':27, '15':22,'19':10, '21':9, '23':11\
            ,'29':5, '31':6, '33':33, '35':19, '37':26, '12':18, '25':8, '26':7, '32':12,\
            '36':16, '38':20, '40':21}
SENSOR_CONDITION = {"High":1, "Low":0}
showCrosshair = False # Don't display grid
fromCenter = False # Select top-left to button-right
#################################################

def executeCollectData(json_file, camera, os_type, windows):
    
    file_name = os.path.split(json_file)[-1]
    if exists(file_name):
        camera.__del__()
        windows.destroy()
        
        
        collect = collectImageOrVideo(json_file=file_name, os_type=os_type)
        collect.collect()
        
        from collectData.image_collect_GUI import collectImageGUI
        collectImageGUI(os_type=os_type, json_file=file_name)
        
        
    else:
        msg.showerror("Don't execute", "The file isn't existing!\nPlease create new file.")

def testPIN(pin):
    import RPi.GPIO as GPIO
    if pin == "Choose Sensor Pin":
        msg.showerror("Input error", "Must save or cut image")
    else:
        pin_number = GPIO_PIN[pin] 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_number, GPIO.IN)
        sleep(0.1)
        msg.showinfo("Pin's potential", "It is {}".format(GPIO.input(pin_number)))


def checkDigit(text, using='float', content=None, last_check=True):

    try:
        if len(text) == 0:
            return True and last_check
        else:
            if using == "float":
                temp = float(text)
            elif using == "int":
                temp = int(text)
            return True and last_check
    except ValueError:
        msg.showerror("Input error", "{} must is {}!".format(content, using))
        return False
        

def CheckUserInput(stringVars:dict):

    check_pass = True

    if len(stringVars['Project_name'].get()) == 0 or len(stringVars["FTP_IP"].get()) == 0 or\
            len(stringVars["user"].get()) == 0 or len(stringVars["password"].get()) == 0:
        check_pass = False
    
    ftp_ip = stringVars['FTP_IP'].get()
    if not re.search(IP_RELU, ftp_ip):
       msg.showwarning("Input error", "The FTP IP isn't OA or FAB.")
       check_pass = False
    
    # 0 is hardware, 1 is software
    if stringVars["condition"].get() == 0:
        if stringVars['sensor'].get() == "Choose Sensor Pin":
            msg.showerror("Input error", "Sensor Pin must set!")
            check_pass = False
        
        if stringVars['sensor_condition'].get() == "Choose condition":
            msg.showerror("Input error", "Sensor condition must set!")
            check_pass = False

    elif stringVars["condition"].get() == 1:
        if stringVars['path'] is None:
            msg.showerror("Input error", "Must save or cut image")
            check_pass = False
            
    if str.isdigit(stringVars['video_time'].get()) or len(stringVars['video_time'].get()) == 0:
        if int(stringVars['video_time'].get()) > 60:
            msg.showerror("Max error", "The video time maximum is 60.")
            check_pass = False
    else:
        msg.showerror("Input error", "Video time must is digit!")
        check_pass = False
    
    
    check_pass = checkDigit(stringVars['interval_time'].get(), content="Interval time", last_check=check_pass)
    check_pass = checkDigit(stringVars['delay_time'].get(), content="Delay time", last_check=check_pass)
    check_pass = checkDigit(stringVars['continous_cut'].get(), using='int', content="Continous cut", last_check=check_pass)
    check_pass = checkDigit(stringVars["threshold"].get(), content="Threshold", last_check=check_pass)
    if check_pass and (float(stringVars["threshold"].get()) > 1 or float(stringVars["threshold"].get()) < 0) :
        msg.showerror("Input error", "Threshold must between 0 and 1!")
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
            show_text += "ROI: Use {} roi\n".format(len(stringVars['roi']))
        
            if stringVars['cut_mode'].get() == 'SSIM':
                show_text += "Compare cut image's SSIM\n"
            elif stringVars['cut_mode'].get() == 'Template':
                show_text += "Compare Template\n"
        
        if stringVars['sensor'].get() != "Choose Sensor Pin":
            show_text += "Sensor PIN:{}\n".format(stringVars['sensor'].get())
        
        if stringVars['sensor_condition'].get() != "Choose condition":
            show_text += "Sensor condition:{}\n".format(stringVars['sensor_condition'].get())
        
        if len(stringVars['video_time'].get()) > 0:
            show_text += "Video time:{}\n".format(stringVars['video_time'].get())
        
        if len(stringVars['interval_time'].get()) > 0:
            show_text += "Interval time:{}\n".format(stringVars['interval_time'].get())
        
        if len(stringVars['delay_time'].get()) > 0:
            show_text += "Delay time:{}\n".format(stringVars['delay_time'].get())
        
        if len(stringVars['continous_cut'].get()) > 0:
            show_text += "Continous cut:{}\n".format(stringVars['continous_cut'].get())

        if len(stringVars["threshold"].get()) > 0:
            show_text += "Threshold: {}\n".format(stringVars["threshold"].get())
        
        if len(stringVars["project_id"].get()) > 0:
            show_text += "Project ID:{}\n".format(stringVars["project_id"].get())

        msg_box = msg.askyesno("Created Check", show_text)
        if msg_box:
            if os.path.exists(stringVars['Project_name'].get() + ".json"):
                exist_box = msg.askyesno("Exist", "The Json file is existing!\nDo you want to cover?")
                if exist_box:
                    writeJson(stringVars)
            else:
                writeJson(stringVars)

def writeJson(stringVars:dict):

    data = {}
    path = os.path.split(stringVars['Project_name'].get())
    file_name = path[1] + ".json"
    if len(path) == 0:
        data["folder"] = ""
    else:
        data["folder"] = path[0]

    data["project name"] = path[1] #stringVars['Project_name'].get()
    data["FTP"] = stringVars['FTP_IP'].get()
    data["user"] = stringVars['user'].get()
    data["password"] = stringVars["password"].get()

    if stringVars["method"].get() == 0:
        data["method"] = "image"
    elif stringVars["method"].get() == 1:
        data["method"] = "video"
    
    if stringVars["condition"].get() == 0:
        data["trigger"] = "hardware"
        data["sensor"] = GPIO_PIN[stringVars["sensor"].get()]
        data["sensor condition"] = SENSOR_CONDITION[stringVars['sensor_condition'].get()]
    elif stringVars["condition"].get() == 1 or stringVars["condition"].get() == 2:
        if stringVars["condition"].get() == 1:
            data["trigger"] = "software"
        else:
            data["trigger"] = "double"
        data["path"] = stringVars["path"]
        if stringVars["roi"] is None:
            data["Used_roi"] = False
        else:
            data["Used_roi"] = True
            data["roi"] = stringVars["roi"]
    
    if stringVars['cut_mode'].get() == 'SSIM':
        data["SSIM"] = True
    elif stringVars['cut_mode'].get() == 'Template':
        data["SSIM"] = False
    
    if data['method'] == "video":
        if len(stringVars["video_time"].get()) == 0:
            data["video_time"] = 60
        else:
            data["video_time"] = int(stringVars["video_time"].get())
    
    if len(stringVars["interval_time"].get()) == 0:
        data["interval"] = 0
    else:
         data["interval"] = float(stringVars["interval_time"].get())
    
    if len(stringVars["delay_time"].get()) == 0:
        data["delay"] = 0
    else:
         data["delay"] = float(stringVars["delay_time"].get())

    if len(stringVars["continous_cut"].get()) == 0:
        data['continous_cut'] = 0
    else:
        data['continous_cut'] = int(stringVars['continous_cut'].get())
    
    if len(stringVars["threshold"].get()) == 0:
        data["threshold"] = 0
    else:
        data["threshold"] = float(stringVars["threshold"].get())

    if len(stringVars["project_id"].get()) == 14:
        data["project_id"] = stringVars["project_id"].get()
    else:
        data["project_id"] = ""

    data["resolution"] = stringVars["resolution"].get()

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
        from picamera.array import PiRGBArray
        from picamera import PiCamera
        self.camera = PiCamera(sensor_mode=0)
        #self.camera.resolution = (1920, 1080) #(3280, 2464)#3280x2464
        #self.camera.framerate = 15
        self.rawCapture = PiRGBArray(self.camera)
        sleep(0.1)
        
    def get_frame(self):
        self.camera.capture(self.rawCapture, format='rgb', use_video_port=True)
        image =self.rawCapture.array
        #print(image.shape)
        self.rawCapture.truncate(0)
        return image
    
    def set_camera(self, resolution):
        if resolution == "Low":
            self.camera.resolution = "1296x972"
            self.camera.framerate = 30
        elif resolution == "Normal":
            self.camera.resolution = "1920x1080"
            self.camera.framerate = 30
        elif resolution == "High":
            self.camera.resolution = "2592x1944"
            self.camera.framerate = 15
        elif resolution == "Maximum":
            self.camera.resolution = "3280x2464"
    
    def __del__(self):
        self.camera.close()

class VideoCaptureWebCamera():
    
    def __init__(self):
        try:
            self.camers = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
            #self.camers = cv2.VideoCapture("./videos/Arcing/2021-11-10 165740.mp4")
        except Exception as e:
            print(e)
    
    def get_frame(self):
        cap, frame = self.camers.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #sleep(0.1)
        return frame

    def set_camera(self, resolution):
        
        if resolution == "Normal":
            self.camers.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camers.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        elif resolution == "Maximum":
            self.camers.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camers.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        
    def __del__(self):
        self.camers.release()    

# Implement selectROI
class drawRoI:

    def __init__(self, width, height):

        self.drawing = False
        self.xmin = 0
        self.ymin = 0
        self.xmax = 0
        self.ymax = 0
        self.rects = []
        self.width = width
        self.height = height
    
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
            self.checkEdge()
            self.rects.append([self.xmin, self.ymin, self.xmax, self.ymax])
            #self.rects.append([int(self.xmin * self.rate_w), int(self.ymin * self.rate_h), int(self.xmax * self.rate_w), int(self.ymax * self.rate_h)])
        elif event == cv2.EVENT_RBUTTONDOWN:
            if len(self.rects) > 0:
                self.rects.pop()
                self.clone_image = self.original_image.copy()
                for rect in self.rects:
                    cv2.rectangle(self.clone_image, (rect[0], rect[1]), (rect[2], rect[3]), (0, 0, 255), 2)
                    #cv2.rectangle(self.clone_image, (int(rect[0]/self.rate_w), int(rect[1]/self.rate_h)), (int(rect[2]/self.rate_w), int(rect[3]/self.rate_h)), (0, 0, 255), 2)
                self.temp_image = self.clone_image
                
    def show_image(self):
        return self.clone_image

    def checkEdge(self):
        
        if self.xmax < self.xmin:
            temp = self.xmax
            self.xmax = self.xmin
            self.xmin = temp

        if self.ymax < self.ymin:
            temp = self.ymax
            self.ymax = self.ymin
            self.ymin = temp

        if self.xmin < 0:
            self.xmin = 0
        
        if self.ymin < 0:
            self.ymin = 0

        if self.xmax > self.width:
            self.xmax = self.width - 1
        
        if self.ymax > self.height:
            self.ymax = self.height - 1
        
        

    def get_rectangle(self):
        if len(self.rects) == 0:
            raise ValueError("Need select ROI.")
        return self.rects

    def call(self, frame, win_name="Cut Image"):
        self.original_image = frame
        self.temp_image = frame.copy()
        self.clone_image = self.original_image.copy()
        
        #cv2.namedWindow("Cut Image")
        cv2.setMouseCallback(win_name, self.draw)