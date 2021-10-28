import queue
import cv2
import os
import json
from ftplib import FTP, error_perm
from datetime import date, datetime
from time import sleep
import numpy as np
from queue import Queue 
import logging
from logging import FileHandler
###################################################
THRESHOLD = 0.9
FPS = 10
#logging.basicConfig(level=logging.INFO,
#        handlers=[logging.FileHandler(filename="log.txt", encoding='utf-8', mode="a+")],
#        format='[%(asctime)s %(levelname)-8s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
###################################################

class collectImageOrVideo:
    def __init__(self, json_file, os='pi'):
        
        self.settings = self.readJson(json_file)
        if os == 'pi':
            from skimage.measure import compare_ssim as ssim
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            import RPi.GPIO as GPIO
            from collectData.GUI_commond import VideoCapture
            #self.camera = VideoCapture()
            
            self.camera = PiCamera(sensor_mode=0)
            self.PiRGBArray = PiRGBArray(self.camera)
            if self.settings["resolution"] == "Low":
                self.camera.resolution = "1296x972"
                self.video_port = True
                self.camera.framerate = 30
            elif self.settings["resolution"] == "Normal":
                self.camera.resolution = "1920x1080"
                self.camera.framerate = 30
                self.video_port = True
            elif self.settings["resolution"] == "High":
                self.camera.resolution = "2592x1944"
                self.camera.framerate = 15
                self.video_port = True
            elif self.settings["resolution"] == "Maximum":
                self.camera.resolution = "3280x2464"
                self.video_port=False
            #self.camera.resolution = self.settings["resolution"]#(3280, 2464)
            #self.camera.framerate = 15
            
            self.ssim = ssim
            self.GPIO = GPIO
        elif os == 'windows':
            from skimage.measure import compare_ssim as ssim
            self.ssim = ssim
            self.camera = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
            if self.settings["resolution"] == "Normal":
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            elif self.settings["resolution"] == "Maximum":
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
        else:
            raise ValueError("`os` must is `pi` or `windows`")
        self.os = os
        self.double_trigger = False
        self.fps_numbers = 0
        self.video_fps = 0 # writer in video frame numbers 
        self.out = None # video writer
        self.fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        self.resize_h, self.resize_w = 0, 0
        self.path = None
        self.video_writer = False
        self.image_writer = False
        self.check_time = datetime.now()
        self.start_time = None
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        format = '[%(asctime)s %(levelname)-8s] %(message)s'
        self.formatter = logging.Formatter(format, datefmt="%Y-%m-%d %H:%M:%S")
        
        self.openLoggingFile()
        '''
        try:
            self.FTPConnect()
            self.FTPMkdir(self.settings['project name'])
            self.ftp.quit()
        except Exception as e:
            self.logger.warning("Connect failed: {}".format(e))
            pass
        except error_perm as msg:
            self.logger.warning("Connect failed: {}".format(msg))
            pass
        '''
        self.closeLoggingFile()

        self.ti = None
        self.queue = Queue()

        self.today = None
        self.video_time = 0 if self.settings['method'] == "image" else int(self.settings["video_time"])
        self.interval_time = int(self.settings['interval'])
        self.delay_time = int(self.settings['delay'])
        self.trigger = self.settings['trigger']

        if self.settings['trigger'] == 'software' or self.settings['trigger'] == 'double':
            self.condition_image = cv2.imread(self.settings['path'])
            self.condition_image = cv2.cvtColor(self.condition_image, cv2.COLOR_BGR2RGB)
            self.condition_image = cv2.blur(self.condition_image, (5, 5))
        else:
            self.condition_image = None
        
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

    def openLoggingFile(self):
        self.file_hanlder = FileHandler(filename="log.txt", encoding='utf-8', mode="a")
        self.file_hanlder.setFormatter(self.formatter)
        self.logger.addHandler(self.file_hanlder)

    def closeLoggingFile(self):
        handler = self.logger.handlers[:]
        for h in handler:
            h.close()
            self.logger.removeHandler(h)
    
    def readJson(self, json_file):
        with open(json_file, "r", encoding='utf-8') as f:
            return json.load(f)

    def FTPConnect(self):
        try:
            self.ftp = FTP()
            self.ftp.connect(self.settings['FTP'], 21)
            self.ftp.login(self.settings['user'], self.settings['password'])
        except Exception as e:
            self.logger.warning("Connect failed: {}".format(e))
            pass
        except error_perm as msg:
            self.logger.warning("Connect failed: {}".format(msg))
            pass
    
    def FTPUpload(self, files):
        try:
            self.FTPConnect()
            self.FTPMkdir(self.settings['project name'])
            self.FTPMkdir(self.today)
            for f in files:
                im = open(f, 'rb')
                self.ftp.storbinary("STOR {}".format(f), im)
                im.close()
                if f != "log.txt":
                    os.remove(f)
            self.ftp.quit()
            
        except Exception as e:
            self.logger.warning("Upload failed : {}".format(e))
            pass
        except error_perm as msg:
            self.logger.warning("Upload failed : {}".format(msg))
            pass

    def FTPMkdir(self, folder):
        try:
            if folder not in self.ftp.nlst():
                self.ftp.mkd(folder)
                self.ftp.cwd(folder)
            else:
                self.ftp.cwd(folder)
        except Exception as e:
            self.logger.warning("Make directory failed : {}".format(e))
            pass
        except error_perm as msg:
            self.logger.warning("Make directory failed : {}".format(msg))
            pass

    def caluateSSIMAndTemplate(self, frame,  choice='SSIM'):
        
        
        storages = []
        frame = cv2.blur(frame, (5, 5))
        if choice == 'SSIM':
            
            score = self.ssim(frame, self.condition_image, multichannel=True)
            if score >= THRESHOLD:
                #logging.info("SSIM trigger success: {:.2f}".format(score))
                self.logger.info("SSIM trigger success: {:.2f}".format(score))
                return True
            else:
                return False
        elif choice == 'Template':
            for roi in self.condition_roi:
                
                template = self.condition_image[roi[1]:roi[3], roi[0]:roi[2]]
                if self.settings['SSIM']:
                    score = self.ssim(frame[roi[1]:roi[3], roi[0]:roi[2]], template, multichannel=True)
                    if score >= THRESHOLD:
                        storages.append("True")
                else:
                    res = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    if min_val <= (1 - THRESHOLD):
                        storages.append("True")
                    
            if len(storages) == len(self.condition_roi):
                if self.settings['SSIM']:
                    self.logger.info("Regoin SSIM trigger success")
                else:
                    self.logger.info("Template trigger success")
                return True
            return False
        else:
            raise ValueError("`choice` must is `SSIM` or `Template`.")
    
    def imageStorage(self, frame=None, queue=False):
        if not queue:
            
            cv2.imwrite(self.path, frame)
            #self.FTPUpload([self.path])
            #self.path = None
        else:
            i = 0
            images = []
            while not self.queue.empty():
                cv2.imwrite(self.path[:-4] + "_" + str(i) + ".jpg", self.queue.get())
                images.append(self.path[:-4] + "_" + str(i) + ".jpg")
                i += 1
            self.FTPUpload(images)
        self.path = None
        self.last_time = self.now_time
        self.check_time = self.now_time

    def videoStorage(self):
        while not self.queue.empty():
            frame = cv2.resize(self.queue.get(), (self.resize_w, self.resize_h))
            self.out.write(frame)

    def judgeData(self, frame):
  
        if self.settings['trigger'] == 'software':
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
                    self.ti = datetime.now()
                    self.out = cv2.VideoWriter(self.path, self.fourcc, FPS, (self.resize_w, self.resize_h))
                    self.fps_numbers = FPS * self.video_time
                    self.video_fps = 0
                    self.video_writer = True
        elif self.settings['trigger'] == 'hardware':
            if self.GPIO.input(self.sensor_pin) == self.condition_sensor:
                self.logger.info("Hardware trigger success: {}".format(self.condition_sensor))
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
        elif self.settings['trigger'] == 'double':
            if self.condition_roi is None:
                choice = "SSIM"
            else:
                choice = "Template"
            
            if self.caluateSSIMAndTemplate(frame, choice=choice):
                self.double_trigger = True
            elif self.double_trigger:
                #logging.info("Double trigger success")
                if self.delay_time > 0:
                    sleep(self.delay_time)
                
                if self.settings['method'] == 'image':
                    self.image_writer = True
                    self.path = self.now_time.strftime("%H%M%S") + ".jpg"

    def collect(self):
        cv2.namedWindow("Execute", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Execute", 640, 480)
        if self.os == 'pi':
            for image in self.camera.capture_continuous(self.PiRGBArray, format="rgb", use_video_port=self.video_port):
                
                self.openLoggingFile()

                frame = image.array
                display_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
                #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                self.now_time = datetime.now()
                if self.today is None:
                    self.today = self.now_time.strftime("%Y-%m-%d")
                elif self.today != self.now_time.strftime("%Y-%m-%d"):
                    
                    self.closeLoggingFile()
                    self.FTPUpload(["log.txt"])
                    os.remove("log.txt")
                    self.today = self.now_time.strftime("%Y-%m-%d")
                    self.openLoggingFile()
                
                if self.image_writer:
                    if self.settings['continous_cut'] <= 1:
                        self.image_writer = False
                        self.imageStorage(display_frame)
                        self.double_trigger = False
                    else:
                        self.video_fps += 1
                        self.queue.put(display_frame)
                        if self.video_fps >= self.settings['continous_cut']:
                            self.image_writer = False
                            self.video_fps = 0
                            self.imageStorage(queue=True)
                            self.double_trigger = False
                elif self.video_writer:
                    self.video_fps += 1
                    self.queue.put(display_frame)
                    if self.video_fps >= self.fps_numbers:
                        self.video_writer = False
                        self.videoStorage()
                        self.out.release()
                        self.video_fps = 0
                        self.FTPUpload([self.path])
                else:
                    if self.last_time is None:
                        #pass
                        self.judgeData(frame)
                    else:
                        seconds = (self.now_time - self.last_time).seconds
                        if seconds >= self.interval_time:
                            self.judgeData(frame)
                    

                cv2.imshow("Execute", display_frame)
                key = cv2.waitKey(1) & 0xFF
                self.PiRGBArray.truncate(0)
                if (datetime.now() - self.check_time).seconds >= 600:
                    self.regularCheck(frame)
                    self.check_time = datetime.now()
                self.closeLoggingFile()
                #self.FTPUpload(["log.txt"])
                if key == ord('q'):
                    break

            cv2.destroyAllWindows()
            self.camera.close()
        else:
            while True:
                
                self.now_time = datetime.now()
                ret, frame = self.camera.read()
                self.openLoggingFile()
                display_frame = frame.copy()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.today is None:
                    self.today = self.now_time.strftime("%Y-%m-%d")
                elif self.today != self.now_time.strftime("%Y-%m-%d"):
                    
                    self.closeLoggingFile()
                    self.FTPUpload(["log.txt"])
                    os.remove("log.txt")
                    self.today = self.now_time.strftime("%Y-%m-%d")
                    self.openLoggingFile()
                
                if self.image_writer:
                    if self.settings['continous_cut'] <= 1:
                        self.image_writer = False
                        self.imageStorage(display_frame)
                        self.double_trigger = False
                    else:
                        self.video_fps += 1
                        self.queue.put(display_frame)
                        if self.video_fps >= self.settings['continous_cut']:
                            self.image_writer = False
                            self.video_fps = 0
                            self.imageStorage(queue=True)
                            self.double_trigger = False
                elif self.video_writer:
                    self.video_fps += 1
                    self.queue.put(display_frame)
                    if self.video_fps >= self.fps_numbers:
                        self.video_writer = False
                        self.videoStorage()
                        self.out.release()
                        self.video_fps = 0
                        self.FTPUpload([self.path])
                else:
                    if self.last_time is None:
                        #pass
                        self.judgeData(frame)
                    else:
                        seconds = (self.now_time - self.last_time).seconds
                        
                        if seconds >= self.interval_time:
                            self.judgeData(frame)
                

                if (datetime.now() - self.check_time).seconds >= 600:
                    self.regularCheck(frame)
                    self.check_time = datetime.now()
                self.closeLoggingFile()
                self.FTPUpload(["log.txt"])
                
                cv2.imshow("Execute", display_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
            cv2.destroyAllWindows()
            self.camera.release()
    
    def regularCheck(self, frame):

        if self.settings['trigger'] == 'software' or self.settings['trigger'] == 'double':
            if self.condition_roi is None:
                choice = "SSIM"
            else:
                choice = "Template"
            score = self.caluateSSIMAndTemplate(frame, choice=choice)
            self.logger.warning("Don't detection: {} : {:.2f}".format(choice, score))
        elif self.settings['trigger'] == 'hardware':
            self.logger.warning("Don't detection: Potential: {}".format(self.GPIO.input(self.sensor_pin)))

                