import cv2
import os
import json
from ftplib import FTP
from datetime import datetime
from time import sleep
#from skimage.measure import compare_ssim as ssim
from skimage.metrics import structural_similarity as ssim
import numpy as np
#from GUI_commond import VideoCapture
from picamera.array import PiRGBArray
from picamera import PiCamera

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


def read_json(jsonFile="Test1.json"):
    settings = {}

    with open(jsonFile, "r", encoding='utf-8') as f:
        settings = json.load(f)

    return settings


def connect_FTP(IP, user, password, port=21):

    try:
        ftp = FTP()
        ftp.connect(IP, port)
        ftp.login(user, password)
        print("Connect {} success!".format(IP))
        return ftp
    except:
        print("Connect {} failed".format(IP))
        return None


def FTP_mkdir(ftp, folder):

    if folder not in ftp.nlst():
        ftp.mkd(folder)
        ftp.cwd(folder)
    else:
        ftp.cwd(folder)
    return ftp


def FTP_image(frame, image_file, ftp):
    cv2.imwrite(image_file, frame)
    #im = open(image_file, 'rb')
    #ftp.storbinary("STOR {}".format(image_file), im)
    #im.close()
    #os.remove(image_file)


def FTP_video(camera, video_time, video_file, ftp):
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    
    out = cv2.VideoWriter(video_file, fourcc, FPS, (640, 480))
    frame_numbers = FPS * video_time
    i = 0
    while i<frame_numbers:
        ret, frame = camera.read()
        out.write(frame)
        i+=1
    out.release()
    cv2.destroyAllWindows()
    im = open(video_file, 'rb')
    ftp.storbinary("STOR {}".format(video_file), im)
    im.close()
    os.remove(video_file)
    
def FTPRaspberryPiVideo(video_file, ftp):
    
    im = open(video_file, 'rb')
    ftp.storbinary("STOR {}".format(video_file), im)
    im.close()
    os.remove(video_file)


def caluate_SSIM(frame, condition):
    grayA = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(condition, cv2.COLOR_BGR2GRAY)
    score = ssim(grayA, grayB)
    print(score)
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


def image_storage(frame, last_time, now_time, ftp, interval_time):
    
    if last_time is None:
        FTP_image(frame, now_time.strftime("%H%M%S")+".jpg", ftp)
        last_time = now_time
    else:
        seconds = (now_time - last_time).seconds
        if seconds >= interval_time:
            FTP_image(frame, now_time.strftime("%H%M%S")+".jpg", ftp)
            last_time = now_time
    return last_time


def video_storage(camera, last_time, now_time, ftp, interval_time, video_time):
    if last_time is None:
        FTP_video(camera, video_time=video_time, video_file=now_time.strftime("%H%M%S")+".mp4", ftp=ftp)
        last_time = now_time
    else:
        seconds = (now_time - last_time).seconds
        if seconds >= interval_time:
            FTP_video(camera, video_time=video_time, video_file=now_time.strftime("%H%M%S")+".mp4", ftp=ftp)
            last_time = now_time    
    return last_time


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

    
def collect_Data(json_file):

    settings = read_json(json_file)
    ftp = connect_FTP(IP=settings['FTP'], user=settings["user"], password=settings['password'])
    ftp = FTP_mkdir(ftp, settings['project name'])
    
    
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

    cameras = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cameras.read()
        today_folder = now_time.strftime("%Y-%m-%d")
        ftp = FTP_mkdir(ftp, today_folder)

        if condition_roi is None and condition_image is not None:
            score = caluate_SSIM(frame, condition_image)
            
            if score >= THRESHOLD:
                if delay_time > 0:
                    sleep(delay_time)
                
                if settings['method'] == "image":
                    ret, frame = cameras.read()
                    last_time = image_storage(frame, last_time=last_time, now_time=now_time, ftp=ftp, interval_time=interval_time)
                else:
                    video_storage(cameras, last_time=last_time, now_time=now_time, ftp=ftp, interval_time=interval_time, video_time=video_time)   
        elif condition_roi is not None:
            if caluate_match(frame, condition_image, condition_roi):
                if delay_time > 0:
                    sleep(delay_time)
                
                if settings['method'] == "image":
                    ret, frame = cameras.read()
                    last_time = image_storage(frame, last_time=last_time, now_time=now_time, ftp=ftp, interval_time=interval_time)
                else:
                    video_storage(cameras, last_time=last_time, now_time=now_time, ftp=ftp, interval_time=interval_time, video_time=video_time)

        
        now_time = datetime.now()
        ftp.cwd("../")
        cv2.imshow("Execute", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cameras.release()
    cv2.destroyAllWindows()



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
            image = cv2.resize(image, (resize_w, reisze_h))
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
