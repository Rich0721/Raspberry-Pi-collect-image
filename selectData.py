import cv2
import os
import json
from ftplib import FTP
from datetime import datetime
from time import sleep
#from skimage.measure import compare_ssim as ssim
#from skimage.metrics import structural_similarity as ssim
import numpy as np
#from GUI_commond import VideoCapture
#from picamera.array import PiRGBArray
#from picamera import PiCamera

###################################################
THRESHOLD = 0.4
FPS = 30
fps_numbers = 0
video_fps = 0 # writer in video frame numbers 
out = None # video writer
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
resize_h, reize_w = 0, 0
video_path = None
###################################################


def FTP_image(frame, image_file, ftp):
    cv2.imwrite(image_file, frame)
    #im = open(image_file, 'rb')
    #ftp.storbinary("STOR {}".format(image_file), im)
    #im.close()
    #os.remove(image_file)

    
def FTPRaspberryPiVideo(video_file, ftp):
    
    im = open(video_file, 'rb')
    ftp.storbinary("STOR {}".format(video_file), im)
    im.close()
    os.remove(video_file)

def caluate_SSIM(frame, condition):
    grayA = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(condition, cv2.COLOR_BGR2GRAY)
    score = ssim(grayA, grayB)
    return score


def caluate_match(frame, condition, rois):

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_condition = cv2.cvtColor(condition, cv2.COLOR_BGR2GRAY)
    storages = []

    for roi in rois:
        template = gray_condition[roi[1]:roi[3], roi[0]:roi[2]]
        
        res = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
        
        loc = np.where( res >= 0.5)
        
        if loc[0].size > 0 and loc[1].size > 0:
            xmin = max(loc[1])
            ymin = max(loc[0])

            storages.append([xmin, ymin])
    
    if len(storages) == len(rois):
        return True
    return False



def videoStorageRaspberryPi(camera, last_time, now_time, ftp, interval_time, video_time):
    if last_time is None:
        
        FTPRaspberryPiVideo(camera, video_time=video_time, video_file=now_time.strftime("%H%M%S")+".mp4", ftp=ftp)
        last_time = now_time
    else:
        seconds = (now_time - last_time).seconds
        if seconds >= interval_time:
            FTPRaspberryPiVideo(camera, video_time=video_time, video_file=now_time.strftime("%H%M%S")+".mp4", ftp=ftp)
            last_time = now_time    
    return last_time


def collectDataRaspberryPi(json_file):
    settings = read_json(json_file)
    ftp = None#connect_FTP(IP=settings['FTP'], user=settings["user"], password=settings['password'])
    #ftp = FTP_mkdir(ftp, settings['project name'])
    writer_video_flag = False
    now_time = datetime.now()
    last_time = None

    video_time = 0 if settings['method'] == "image" else int(settings["video_time"])
    interval_time = int(settings['interval'])
    delay_time = int(settings['delay']) 
    condition_image = cv2.imread(settings['path']) if settings['trigger'] == 'software' else None
    
    if condition_image is not None and settings['Used_roi']:
        condition_roi = settings['roi']
    else:
        condition_roi = None
        
    global fps_numbers, video_fps, out, fourcc, resize_w, reisze_h, video_path
    
    camera = PiCamera()
    #camera.framerate = 32
    rawCapture = PiRGBArray(camera)
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        
        today_folder = now_time.strftime("%Y-%m-%d")
        image = frame.array
        
        #ftp = FTP_mkdir(ftp, today_folder)
        if writer_video_flag:
            image = frame.array
            image = cv2.resize(image, (resize_w, resize_h))
            out.write(image)
            cv2.imshow("test", image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            video_fps += 1
            if video_fps >= fps_numbers:
                writer_video_flag = False
                video_fps = 0
                out.release()
                FTPRaspberryPiVideo(video_path, ftp)
            rawCapture.truncate(0)
            continue
        
        if condition_roi is None and condition_image is not None:
            score = caluate_SSIM(image, condition_image)
            
            if score >= THRESHOLD:
                if delay_time > 0:
                    sleep(delay_time)
                
                if settings['method'] == "image":
                    last_time = image_storage(image, last_time=last_time, now_time=now_time, ftp=ftp, interval_time=interval_time)
                else:
                    fps_numbers = FPS * video_time
                    h, w = image.shape[:2]
                    if h > 1080 and w > 1920:
                        resize_w = 1920
                        resize_h = 1080
                    else:
                        resize_w = w
                        resize_h = h
                    video_path = now_time.strftime("%H%M%S")+".mp4"
                    out = cv2.VideoWriter(video_path, fourcc, FPS, (resize_w, resize_h))
                    image = cv2.resize(image, (resize_w, resize_h))
                    out.write(image)
                    video_fps +=1
                    writer_video_flag = True   
        elif condition_roi is not None:
            if caluate_match(image, condition_image, condition_roi):
                if delay_time > 0:
                    sleep(delay_time)
                
                if settings['method'] == "image":
                    print("123")
                    last_time = image_storage(image, last_time=last_time, now_time=now_time, ftp=ftp, interval_time=interval_time)
                else:
                    
                    fps_numbers = FPS * video_time
                    h, w = image.shape[:2]
                    if h > 1080 and w > 1920:
                        resize_w = 1920
                        resize_h = 1080
                    else:
                        resize_w = w
                        resize_h = h
                    video_path = now_time.strftime("%H%M%S")+".mp4"
                    out = cv2.VideoWriter(video_path, fourcc, FPS, (resize_w, resize_h))
                    image = cv2.resize(image, (resize_w, resize_h))
                    out.write(image)
                    video_fps +=1
                    writer_video_flag = True
        
        now_time = datetime.now()
        #ftp.cwd("../")
        cv2.imshow("Execute", image)
        
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        
        if key == ord('q'):
            break
    
    camera.close()
    cv2.destroyAllWindows()


class collectImageOrVideo:
    def __init__(self, json_file, os='pi'):
        
        if os == 'pi':
            from skimage.metrics import structural_similarity as ssim
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            self.camera = PiCamera()
            self.PiRGBArray = PiRGBArray(self.camera)
        elif os == 'windows':
            from skimage.measure import compare_ssim as ssim
            self.camera = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        
        self.settings = self.readJson(json_file)
        self.fps_numbers = 0
        self.video_fps = 0 # writer in video frame numbers 
        self.out = None # video writer
        self.fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        self.resize_h, self.resize_w = 0, 0
        self.path = None
        self.video_writer = False
        self.FTPConnect()
        #self.ftp = self.FTPConnect()
        self.FTPMkdir(self.settings['project name'])

        self.video_time = 0 if self.settings['method'] == "image" else int(self.settings["video_time"])
        self.interval_time = int(self.settings['interval'])
        self.delay_time = int(self.settings['delay']) 
        self.condition_image = cv2.imread(self.settings['path']) if self.settings['trigger'] == 'software' else None

        if self.condition_image is not None and self.settings['Used_roi']:
            self.condition_roi = self.settings['roi']
        else:
            self.condition_roi = None
        
        if self.condition_image is not None:
            self.condition_image_gray = cv2.cvtColor(self.condition_image, cv2.COLOR_BGR2GRAY)

        if self.settings['trigger'] == 'hardware':
            self.sensor = self.settings['sensor']
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
            #return ftp
        except:
            print("Connect {} failed".format(self.settings['FTP']))
            #return None
    
    def FTPUpload(self):
        im = open(self.path, 'rb')
        self.ftp.storbinary("STOR {}".format(self.path), im)
        im.close()
        os.remove(self.path)
        self.path = None
    
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
            score = ssim(gray_frame, self.condition_image_gray)
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

    def videoStorage(self):
        while self.video_fps < self.fps_numbers:
            ret, frame = self.camera.read()
            frame = cv2.resize(frame, (self.resize_w, self.resize_h))
            self.out.write(frame)
        self.out.release()
        self.video_fps = 0
        self.FTPUpload()

    def collectWindows(self):
        
        #self.FTPMkdir(self.settings['project name'])
        while True:
            self.now_time = datetime.now()
            ret, frame = self.camera.read()
            today_folder = self.now_time.strftime("%Y-%m-%d")
            self.FTPMkdir(today_folder)
            
            if self.condition_roi is None and self.condition_image is not None:
                if self.caluateSSIMAndTemplate(frame, choice='SSIM'):
                    if self.delay_time > 0:
                        sleep(self.delay_time)
                    
                    if self.settings['method'] == 'image':
                        ret, frame = self.camera.read()
                        self.path = self.now_time.strftime("%H%M%S") + ".jpg"
                        self.imageStorage(frame)
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
                        self.videoStorage()
            elif self.condition_roi is not None:
                if self.caluateSSIMAndTemplate(frame, choice='Template'):
                    if self.delay_time > 0:
                        sleep(self.delay_time)
                    
                    if self.settings['method'] == 'image':
                        ret, frame = self.camera.read()
                        self.path = self.now_time.strftime("%H%M%S") + ".jpg"
                        self.imageStorage(frame)
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
                        self.videoStorage()
            self.ftp.cwd("../")
            
            #ftp.cwd("../")
            cv2.imshow("Execute", frame)
            
            key = cv2.waitKey(1) & 0xFF
            #rawCapture.truncate(0)
            
            if key == ord('q'):
                break
        cv2.destroyAllWindows()
        self.camera.release()