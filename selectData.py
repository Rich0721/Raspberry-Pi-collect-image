import cv2
import os
import json
from ftplib import FTP
from datetime import datetime
from time import sleep
import numpy as np

###################################################
THRESHOLD = 0.4
FPS = 30
###################################################

class collectImageOrVideo:
    def __init__(self, json_file, os='pi'):
        
        if os == 'pi':
            from skimage.metrics import structural_similarity as ssim
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            import RPi.GPIO as GPIO
            self.camera = PiCamera()
            self.PiRGBArray = PiRGBArray(self.camera)
            self.ssim = ssim
            self.GPIO = GPIO
        elif os == 'windows':
            from skimage.measure import compare_ssim as ssim
            self.ssim = ssim
            self.camera = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        else:
            raise ValueError("`os` must is `pi` or `windows`")
        self.os = os
        self.settings = self.readJson(json_file)
        self.fps_numbers = 0
        self.video_fps = 0 # writer in video frame numbers 
        self.out = None # video writer
        self.fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        self.resize_h, self.resize_w = 0, 0
        self.path = None
        self.video_writer = False
        self.image_writer = False
        self.FTPConnect()
        
        self.FTPMkdir(self.settings['project name'])

        self.video_time = 0 if self.settings['method'] == "image" else int(self.settings["video_time"])
        self.interval_time = int(self.settings['interval'])
        self.delay_time = int(self.settings['delay'])
        self.trigger = self.settings['trigger']
        self.condition_image = cv2.imread(self.settings['path']) if self.settings['trigger'] == 'software' else None

        if self.condition_image is not None and self.settings['Used_roi']:
            self.condition_roi = self.settings['roi']
        else:
            self.condition_roi = None
        
        if self.condition_image is not None:
            self.condition_image_gray = cv2.cvtColor(self.condition_image, cv2.COLOR_BGR2GRAY)

        if self.settings['trigger'] == 'hardware':
            self.sensor_pin = self.settings['sensor']
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(self.sensor_pin, self.GPIO.IN)
            self.condition_sensor = self.settings['sensor condition']
        self.now_time = None
        self.last_time = None

    def readJson(self, json_file):
        with open(json_file, "r", encoding='utf-8') as f:
            return json.load(f)

    def FTPConnect(self):
        try:
            self.ftp = FTP()
            self.ftp.connect(self.settings['FTP'], 21)
            self.ftp.login(self.settings['user'], self.settings['password'])
            print("Connect {} success!".format(self.settings['FTP']))
        except:
            print("Connect {} failed".format(self.settings['FTP']))
    
    def FTPUpload(self):
        try:
            im = open(self.path, 'rb')
            self.ftp.storbinary("STOR {}".format(self.path), im)
            im.close()
            print("Upload success!")
            os.remove(self.path)
            self.path = None
        except:
            print("Upload failed!")
            pass

    def FTPMkdir(self, folder):
        if folder not in self.ftp.nlst():
            self.ftp.mkd(folder)
            self.ftp.cwd(folder)
        else:
            self.ftp.cwd(folder)
    
    def caluateSSIMAndTemplate(self, frame,  choice='SSIM'):
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        storages = []

        if choice == 'SSIM':
            score = self.ssim(gray_frame, self.condition_image_gray)
            if score >= THRESHOLD:
                return True
            else:
                return False
        elif choice == 'Template':
            for roi in self.condition_roi:
                template = self.condition_image_gray[roi[1]:roi[3], roi[0]:roi[2]]
                
                res = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
                loc = np.where( res >= THRESHOLD)
                
                if loc[0].size > 0 and loc[1].size > 0:
                    xmin = max(loc[1])
                    ymin = max(loc[0])

                    storages.append([xmin, ymin])
                
                if len(storages) == len(self.condition_roi):
                    
                    return True
                return False
        else:
            raise ValueError("`choice` must is `SSIM` or `Template`.")
    
    def imageStorage(self, frame):

        if self.last_time is None:
            cv2.imwrite(self.path, frame)
            self.FTPUpload()
            self.last_time = self.now_time
        else:
            seconds = (self.now_time - self.last_time).seconds
            if seconds >= self.interval_time:
                cv2.imwrite(self.path, frame)
                self.FTPUpload()
                self.last_time = self.now_time

    def videoStorage(self, frame):
        frame = cv2.resize(frame, (self.resize_w, self.resize_h))
        self.out.write(frame)

    def judgeData(self, frame):
        if self.image_writer:
                self.image_writer = False
                self.imageStorage(frame)
        elif self.video_writer:
            self.video_fps += 1
            self.videoStorage(frame)
            if self.video_fps >= self.fps_numbers:
                self.video_writer = False
                self.out.release()
                self.video_fps = 0
                self.FTPUpload() 
        elif self.settings['trigger'] == 'software':
            # trigger is software has 2 method that collect data
            if self.condition_roi is None:
                choice = "SSIM"
            else:
                choice = "Template"

            if self.caluateSSIMAndTemplate(frame, choice=choice):
                if self.delay_time > 0:
                    sleep(self.delay_time)
                
                if self.settings['method'] == 'image':
                    self.image_writer = True
                    self.path = self.now_time.strftime("%H%M%S") + ".jpg"
                else:
                    self.path = self.now_time.strftime("%H%M%S") + ".mp4"
                    h, w = frame.shape[:2]
                    if h > 1080 and w >1920:
                        self.resize_w = 1920
                        self.resize_h = 1080
                    else:
                        self.resize_w = w
                        self.resize_h = h
                    self.out = cv2.VideoWriter(self.path, self.fourcc, FPS, (self.resize_w, self.resize_h))
                    self.fps_numbers = FPS * self.video_time
                    self.video_fps = 0
                    self.video_writer = True
        elif self.settings['trigger'] == 'hardware':
            if self.GPIO.input(self.sensor_pin) == self.condition_sensor:
                
                if self.delay_time > 0:
                    sleep(self.delay_time)
                    
                if self.settings['method'] == 'image':
                    self.image_writer = True
                    self.path = self.now_time.strftime("%H%M%S") + ".jpg"
                else:
                    self.path = self.now_time.strftime("%H%M%S") + ".mp4"
                    h, w = frame.shape[:2]
                    if h > 1080 and w >1920:
                        self.resize_w = 1920
                        self.resize_h = 1080
                    else:
                        self.resize_w = w
                        self.resize_h = h
                    self.out = cv2.VideoWriter(self.path, self.fourcc, FPS, (self.resize_w, self.resize_h))
                    self.fps_numbers = FPS * self.video_time
                    self.video_fps = 0
                    self.video_writer = True

    def collect(self):
        if self.os == 'pi':
            for image in self.camera.capture_continuous(self.PiRGBArray, format="bgr", use_video_port=True):
                frame = image.array
                self.now_time = datetime.now()
                today_folder = self.now_time.strftime("%Y-%m-%d")
                self.FTPMkdir(today_folder)
                self.judgeData(frame)
                
                cv2.imshow("Execute", frame)
                key = cv2.waitKey(1) & 0xFF
                self.ftp.cwd("../")
                self.PiRGBArray.truncate(0)
                if key == ord('q'):
                    break

            cv2.destroyAllWindows()
            self.camera.close()
        else:
            while True:
                self.now_time = datetime.now()
                ret, frame = self.camera.read()
                today_folder = self.now_time.strftime("%Y-%m-%d")
                self.FTPMkdir(today_folder)
                self.judgeData(frame)
                
                cv2.imshow("Execute", frame)
                key = cv2.waitKey(1) & 0xFF
                self.ftp.cwd("../")
                if key == ord('q'):
                    break
                
            cv2.destroyAllWindows()
            self.camera.release()