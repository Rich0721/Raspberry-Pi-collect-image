#!/usr/bin/env python3
# -*- coding: utf-8 -**
"""
Created on Thu Oct 14 10:17:52 2021

@author: pi
"""

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
from datetime import datetime

camera = PiCamera()
video_length = 60
camera.resolution = "640x480"
camera.framerate = 40
rawCapture = PiRGBArray(camera)
cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Test", 640, 480)
now = None
i = 0
video_frame = []
try:
    for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = image.array
        video_frame.append(frame)
        
        i+= 1
        if now is None:
            now = datetime.now()
        #(datetime.now()-now
        elif (datetime.now()-now).seconds > video_length:
            filename = now.strftime("%Y-%m-%d %H%M%S") + ".avi"
            print(filename)
            out = cv2.VideoWriter("./videos/" + filename,cv2.VideoWriter_fourcc('M','J','P','G'), len(video_frame)//video_length, (640,480))
            for i, f in enumerate(video_frame):
                out.write(f)
            out.release()
            video_frame.clear()
            now = datetime.now()
        
        cv2.imshow("Test", frame)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        if key == ord('q'):
            break
except Exception as e:
    print(e)

cv2.destroyAllWindows()           
camera.close()