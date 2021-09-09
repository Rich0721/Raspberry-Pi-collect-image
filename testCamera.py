#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 09:36:47 2021

@author: pi
"""

from skimage.metrics import structural_similarity as ssim
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
from GUI_commond import VideoCapture
import cv2
from time import sleep
import json

def nothing(x):
    pass

def writeJson(brightness, saturation, shutter, iso):
    
    data = {}
    data['brightness'] = brightness
    data['saturation'] = saturation
    data['shutter'] = shutter
    data['iso'] = iso
    
    with open("camera_set.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    


if __name__ == "__main__":
    
    write = True
    camera = PiCamera(sensor_mode=0)
    PiRGBArray = PiRGBArray(camera)
    camera.framerate = 30
    cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Brightness", "Test", 0, 100, nothing)
    cv2.createTrackbar("Saturation", "Test", 150, 200, nothing)
    cv2.createTrackbar("Shutter speed", "Test", 0, 10000000, nothing)
    cv2.createTrackbar("ISO", "Test", 0, 800, nothing)
    
    
    #cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Test", 640, 480)
    sleep(0.1)
    for image in camera.capture_continuous(PiRGBArray, format="bgr", use_video_port=True):
        frame = image.array
        #print(frame)
        try:
            if camera.iso != cv2.getTrackbarPos("ISO", "Test"):
                camera.iso = cv2.getTrackbarPos("ISO", "Test")
            elif camera.saturation != cv2.getTrackbarPos("Saturation", "Test"):
                camera.saturation = cv2.getTrackbarPos("Saturation", "Test") - 100
            elif camera.brightness != cv2.getTrackbarPos("Brightness", "Test"):
                camera.brightness = cv2.getTrackbarPos("Brightness", "Test")
            elif camera.shutter_speed != cv2.getTrackbarPos("Shutter speed", "Test"):
                camera.shutter_speed = cv2.getTrackbarPos("Shutter speed", "Test")  
        except:
            write = False
            cv2.destoryAllWindows()
            break
        cv2.imshow("Test", frame)
        
        PiRGBArray.truncate(0)
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break
    
    if write:
        writeJson(camera.brightness, camera.saturation, camera.shutter_speed, camera.iso)
    
    camera.close()