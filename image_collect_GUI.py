import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font
from PIL import ImageTk, Image
from GUI_commond import  CheckUserInput, drawRoI, executeCollectData, testPIN
from PIL import ImageTk, Image
import cv2
import os
from glob import glob
import json
#from picamera.array import PiRGBArray
#from picamera import PiCamera

###########################################
TITLE_NAME_FONT = ('Times', 12, 'bold')
BUTTON_FONT = ('Times', 10)
PIN_GPIO = {2:'3', 3:'5', 4:'7', 17:'11', 27:'13', 22:'15', 10:'19', 9:'21', 11:'23'\
            ,5:'29', 6:'31', 33:'33', 19:'35', 26:'37', 18:'12', 8:'25', 7:'26', 12:'32',\
            16:'36', 20:'38', 21:'40'}
MODE = {0:"High", 1:"Low"}
###########################################

class collectImageGUI:

    def __init__(self, width=600, height=800, os='pi'):
        
        self.windows = tk.Tk()
        self.windows.title("AUO L7B影像蒐集")
        self.windows.geometry("{}x{}".format(width, height))
        if os == 'pi':
            from GUI_commond import VideoCapture
            self.camera = VideoCapture()
        elif os == 'windows':
            from GUI_commond import VideoCaptureWebCamera
            self.camera = VideoCaptureWebCamera()
        else:
            raise ValueError("os must is `pi` or `windows`")
        self.os = os
        self.image_width = 0
        self.image_height = 0
        self.rate = 1
        self.rate_w = 1
        self.rate_h = 1
        self.path = None
        self.roi = None
        self.photo = None
        self.user_choice_dict = None

        self.setBasicLabel()
        self.delay = 15
        self.update_condition()
        
        self.windows.mainloop()


    def setBasicLabel(self):

        # Set project, FTP, user and password's label and text
        self.basic_set_frame = tk.Frame(self.windows, width=100, height=200)
        self.project_label = tk.Label(self.basic_set_frame, text="Project name", font=TITLE_NAME_FONT)
        self.project_label.grid(column=0, row=0)
        self.project_var = tk.StringVar()
        self.project_text = tk.Entry(self.basic_set_frame, textvariable=self.project_var)
        self.project_text.grid(column=1, row=0)
        self.FTP_label = tk.Label(self.basic_set_frame, text="FTP server IP", font=TITLE_NAME_FONT)
        self.FTP_label.grid(column=2, row=0)
        self.FTP_var = tk.StringVar()
        self.FTP_text = tk.Entry(self.basic_set_frame, textvariable=self.FTP_var)
        self.FTP_text.grid(column=3, row=0)
        self.user_label = tk.Label(self.basic_set_frame, text="user", font=TITLE_NAME_FONT)
        self.user_label.grid(column=0, row=1)
        self.user_var = tk.StringVar()
        self.user_text = tk.Entry(self.basic_set_frame, textvariable=self.user_var)
        self.user_text.grid(column=1, row=1)
        self.password_label = tk.Label(self.basic_set_frame, text="password", font=TITLE_NAME_FONT)
        self.password_label.grid(column=2, row=1)
        self.password_var = tk.StringVar()
        self.password_text = tk.Entry(self.basic_set_frame, textvariable=self.password_var)
        self.password_text.grid(column=3, row=1)
        self.basic_set_frame.pack()

        # Set collect image of method
        self.method_value = tk.IntVar()
        #method_value.set(1)
        self.method_frame = tk.Frame(self.windows, width=100, height=50)
        self.method_label = tk.Label(self.method_frame, text="Collected method" , font=TITLE_NAME_FONT)
        self.method_label.grid(column=0, row=0)
        self.method_image_btn = tk.Radiobutton(self.method_frame, text="image", variable=self.method_value, value=0, font=BUTTON_FONT)
        self.method_image_btn.grid(column=1, row=0)
        self.method_video_btn = tk.Radiobutton(self.method_frame, text='video', variable=self.method_value, value=1, font=BUTTON_FONT)
        self.method_video_btn.grid(column=2, row=0)
        self.method_frame.pack()

        # Set collect image condition
        self.condition_value = tk.IntVar()
        self.condition_frame = tk.Frame(self.windows, width=100, height=250)
        self.condition_label = tk.Label(self.condition_frame, text="Trigger Image", font=TITLE_NAME_FONT)
        self.condition_label.grid(column=0, row=0)
        self.condition_hardware = tk.Radiobutton(self.condition_frame, text="hardware", variable=self.condition_value, value=0, font=BUTTON_FONT)
        self.condition_hardware.grid(column=1, row=0)
        self.condition_software = tk.Radiobutton(self.condition_frame, text="software", variable=self.condition_value, value=1, font=BUTTON_FONT)
        self.condition_software.grid(column=2, row=0)
        self.condition_frame.pack()

        # condition real image
        self.condition_image_frame = tk.Frame(self.windows, width=480, height=320)
        self.condition_image = tk.Label(self.condition_image_frame)
        self.condition_image.grid(column=0, row=0)
        self.condition_image_frame.pack()
        
        self.condition_button_frame = tk.Frame(self.windows, height=20)
        self.condition_cut_button = tk.Button(self.condition_button_frame, text="Cut", font=BUTTON_FONT, command=lambda: self.save_cut_photo(mode="cut"))
        self.condition_cut_button.grid(column=0, row=0)
        
        self.condition_save_button = tk.Button(self.condition_button_frame, text="Save", font=BUTTON_FONT, command=lambda: self.save_cut_photo(mode="save"))
        self.condition_save_button.grid(column=1, row=0)
        self.condition_button_frame.pack()

        # Sensor Pin
        self.sensor_var = tk.StringVar()
        self.sensor_frame = tk.Frame(self.windows, height=20)
        self.sensor_label = tk.Label(self.sensor_frame, text="IR sensor PIN  ", font=TITLE_NAME_FONT)
        self.sensor_label.grid(row=0, column=0)
        self.sensor_text = ttk.Combobox(self.sensor_frame, textvariable=self.sensor_var, values=["Choose Sensor Pin","3", "5", "7", "8", "11", "12", "13", "15", "16", "18", "19", "21", "22",\
                        "23", "24", "26", "29", "31", "32", "33", "35", "36", "37", "38", "40"])
        self.sensor_text.current(0)
        self.sensor_text.grid(row=0, column=1)
        self.sensor_test_button = tk.Button(self.sensor_frame, text="Test", height=1, font=BUTTON_FONT, command=lambda: testPIN(self.sensor_var.get()))
        self.sensor_test_button.grid(row=0, column=2)
        self.sensor_condition_var = tk.StringVar()
        self.sensor_condition_label = tk.Label(self.sensor_frame, text="Collected image using sensor", font=TITLE_NAME_FONT)
        self.sensor_condition_label.grid(row=1, column=0)
        self.sensor_condition_box = ttk.Combobox(self.sensor_frame, textvariable=self.sensor_condition_var, values=["Choose condition", "High", "Low"])
        self.sensor_condition_box.current(0)
        self.sensor_condition_box.grid(row=1, column=1)
        self.cut_mode_var = tk.StringVar()
        self.cut_mode_label = tk.Label(self.sensor_frame, text='Cut mode', font=TITLE_NAME_FONT)
        self.cut_mode_label.grid(row=2, column=0)
        self.cut_mode_choose = ttk.Combobox(self.sensor_frame, textvariable=self.cut_mode_var, values=["SSIM", "Template"])
        self.cut_mode_choose.grid(row=2, column=1, padx=5)
        self.cut_mode_choose.current(0)
        self.camera_resolution_var = tk.StringVar()
        self.camera_resolution_label = tk.Label(self.sensor_frame, text='Resolution', font=TITLE_NAME_FONT)
        self.camera_resolution_label.grid(row=3, column=0)
        self.camera_resolution_choose = ttk.Combobox(self.sensor_frame, textvariable=self.camera_resolution_var, values=["640x480", "1280x720", "1640x922", "1640x1232", "2592x1944", "3280x2464"])
        self.camera_resolution_choose.grid(row=3, column=1)
        self.camera_resolution_choose.current(0)
        
        self.sensor_frame.pack()

        # other set
        self.other_frame = tk.Frame(self.windows, height=20)
        self.video_time_label = tk.Label(self.other_frame, text="Every video time(sec)", font=TITLE_NAME_FONT)
        self.video_time_label.grid(row=0, column=0)
        self.video_time_var = tk.StringVar()
        self.video_time_var.set(5)
        self.video_time_text = tk.Entry(self.other_frame, textvariable=self.video_time_var)
        self.video_time_text.grid(row=0, column=1)
        self.interval_time_label = tk.Label(self.other_frame, text="Interval time(sec)", font=TITLE_NAME_FONT)
        self.interval_time_label.grid(row=0, column=2)
        self.interval_time_var = tk.StringVar()
        self.interval_time_var.set(0)
        self.interval_time_text = tk.Entry(self.other_frame, textvariable=self.interval_time_var)
        self.interval_time_text.grid(row=0, column=3)
        self.delay_time_label = tk.Label(self.other_frame, text="Delay time(sec)", font=TITLE_NAME_FONT)
        self.delay_time_label.grid(row=1, column=0)
        self.delay_time_var = tk.StringVar(0)
        self.delay_time_var.set(0)
        self.delay_time_text = tk.Entry(self.other_frame, textvariable=self.delay_time_var)
        self.delay_time_text.grid(row=1, column=1)
        self.continuous_label = tk.Label(self.other_frame, text="Continuous Cut", font=TITLE_NAME_FONT)
        self.continuous_label.grid(row=1, column=2)
        self.continuous_var = tk.StringVar(0)
        self.continuous_var.set(0)
        self.continuous_text = tk.Entry(self.other_frame, textvariable=self.continuous_var)
        self.continuous_text.grid(row=1, column=3)
        self.other_frame.pack()
        
        
        self.user_choice_dict = {
            "Project_name": self.project_var,
            "FTP_IP" : self.FTP_var,
            "user": self.user_var,
            "password" : self.password_var,
            "path": None,
            "roi":None,
            "delay_time":self.delay_time_var,
            "sensor": self.sensor_var,
            "video_time": self.video_time_var,
            "interval_time": self.interval_time_var,
            "method": self.method_value,
            "condition":self.condition_value,
            "sensor_condition":self.sensor_condition_var,
            "continous_cut":self.continuous_var,
            "cut_mode":self.cut_mode_var,
            "resolution":self.camera_resolution_var
        }
        
        # Load and create JSON file and execute collect data using JSON file.
        self.button_frame = tk.Frame(self.windows, width=70, height=1)
        self.save_button = tk.Button(self.button_frame, text="Save", height=1, width=5, font=BUTTON_FONT, command=lambda : CheckUserInput(self.user_choice_dict))
        self.save_button.grid(row=0, column=0)
        self.load_button = tk.Button(self.button_frame, text="Load", height=1, width=5, font=BUTTON_FONT, command=self.load_file)
        self.load_button.grid(row=0, column=1)
        self.execute_button = tk.Button(self.button_frame, text="Execute", height=1, width=5, font=BUTTON_FONT, command=lambda:executeCollectData(self.project_var.get()+".json", self.camera, self.os, self.windows))
        self.execute_button.grid(row=0, column=2)
        col_count, row_count = self.button_frame.grid_size()
        for col in range(col_count):
            
            self.button_frame.grid_columnconfigure(col, minsize=100)
        self.button_frame.pack()
        
    def update_condition(self):
        
        if self.condition_value.get() == 0:
            image = Image.open("./basic_image/pi_GPIO.png").resize((480, 270))
            image = ImageTk.PhotoImage(image)
            self.photo = None
        else:
            try:
                self.camera.set_camera(resolution=self.camera_resolution_choose.get())
                frame = self.camera.get_frame()
                if self.user_choice_dict['roi'] is None:
                    h, w = frame.shape[:2]
                else:
                    temp_image = cv2.imread(self.user_choice_dict['path'])
                    h, w = temp_image.shape[:2]
                self.photo = frame
                self.rate = 480 / w
                image = cv2.resize(frame, (480, 270))
                if self.user_choice_dict['roi'] is not None:
                    for roi in self.user_choice_dict['roi']:
                        image = cv2.rectangle(image, (int(roi[0]*self.rate), int(roi[1]*self.rate)), (int(roi[2]*self.rate), int(roi[3]*self.rate)), (255, 0, 0), 2)
                image = ImageTk.PhotoImage(image=Image.fromarray(image))
            except:
                if self.os == 'pi':
                    from GUI_commond import VideoCapture
                    self.camera = VideoCapture()
                elif self.os == 'windows':
                    from GUI_commond import VideoCaptureWebCamera
                    self.camera = VideoCaptureWebCamera()
                image = Image.open("./basic_image/not_connecting.png").resize((480, 270))
                image = ImageTk.PhotoImage(image)
                self.photo = None
            
        self.condition_image.configure(image=image)
        self.condition_image.image = image
        self.windows.after(self.delay, self.update_condition)
    
    def save_cut_photo(self, mode="save"):
        if self.photo is not None:
            images = glob(os.path.join("./condition_images", "condition_*.jpg"))
            self.user_choice_dict["path"] = os.path.join("./condition_images", "condition_" + str(len(images)) + ".jpg")
            frame = cv2.cvtColor(self.photo, cv2.COLOR_RGB2BGR)
            cv2.imwrite(self.user_choice_dict["path"] , frame)
            
            original_h, original_w = frame.shape[:2]
            display_h = 480
            display_w = 640
            if mode == "save":
                cv2.imshow("Save Image", cv2.resize(frame, (display_w, display_h)))
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            elif mode == "cut":
                rate_w = original_w / 640
                rate_h = original_h / 480
                draw = drawRoI(rate_w, rate_h)
                img = cv2.resize(frame, (display_w, display_h))
                draw.call(img)
                
                while True:
                    cv2.imshow("Cut Image", draw.show_image())
                    key = cv2.waitKey(1)
                    
                    # Close program with keyboard 'q'
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        break
                self.user_choice_dict["roi"] = draw.get_rectangle()
    
    def load_file(self):
        filename = fd.askopenfilename(filetypes=[('json files',"*.json")])
        if len(filename) > 0:
            with open(filename, "r", encoding='utf-8') as f:
                array_list = json.load(f)
                self.project_var.set(array_list['project name'])
                self.FTP_var.set(array_list['FTP'])
                self.user_var.set(array_list['user'])
                self.password_var.set(array_list['password'])
                
                if array_list['method'] == 'image':
                    self.method_value.set(0)
                else:
                    self.method_value.set(1)
                    self.video_time_var.set(array_list['video_time'])
                
                if array_list['trigger'] == 'software':
                    self.condition_value.set(1)

                    self.user_choice_dict['path'] = array_list['path']
                    if array_list['Used_roi']:
                        self.user_choice_dict['roi'] = array_list['roi']
                else:
                    self.condition_value.set(0)
                    self.sensor_var.set(PIN_GPIO[array_list['sensor']])
                    self.sensor_condition_var.set(MODE[array_list['sensor condition']])
                
                if array_list['SSIM']:
                    self.cut_mode_choose.current(0)
                else:
                    self.cut_mode_choose.current(1)
                self.interval_time_var.set(array_list['interval'])
                self.delay_time_var.set(array_list['delay'])
                self.continuous_var.set(array_list['continous_cut'])
            

if __name__ == "__main__":
    if not os.path.exists("condition_images"):
        os.mkdir("condition_images")
    GUI = collectImageGUI(os='windows') 