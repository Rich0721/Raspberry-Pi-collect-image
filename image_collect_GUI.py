import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from GUI_commond import  CheckUserInput, VideoCapture, savePhoto, cutPhoto
from PIL import ImageTk, Image
import cv2
#from picamera.array import PiRGBArray
#from picamera import PiCamera

###########################################
TITLE_NAME_FONT = ('Times', 16, 'bold')
BUTTON_FONT = ('Times', 16)
ALARM_FONT = ("Times", 16,  "bold")
###########################################

class collectImageGUI:

    def __init__(self, width=600, height=800):
        
        self.windows = tk.Tk()
        self.windows.title("AUO L7B影像蒐集")
        self.windows.geometry("{}x{}".format(width, height))
        #self.camera = VideoCapture()
        self.image_width = 0
        self.image_height = 0
        self.rate = 1
        self.path = None
        self.roi = []
        self.photo = None

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
        self.FTP_label.grid(column=0, row=1)
        self.FTP_var = tk.StringVar()
        self.FTP_text = tk.Entry(self.basic_set_frame, textvariable=self.FTP_var)
        self.FTP_text.grid(column=1, row=1)
        self.user_label = tk.Label(self.basic_set_frame, text="user", font=TITLE_NAME_FONT)
        self.user_label.grid(column=0, row=2)
        self.user_var = tk.StringVar()
        self.user_text = tk.Entry(self.basic_set_frame, textvariable=self.user_var)
        self.user_text.grid(column=1, row=2)
        self.password_label = tk.Label(self.basic_set_frame, text="password", font=TITLE_NAME_FONT)
        self.password_label.grid(column=0, row=3)
        self.password_var = tk.StringVar()
        self.password_text = tk.Entry(self.basic_set_frame, textvariable=self.password_var)
        self.password_text.grid(column=1, row=3)
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
        self.path_text_var = tk.StringVar()
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
        self.condition_cut_button = tk.Button(self.condition_button_frame, text="Cut", font=BUTTON_FONT, command=lambda :cutPhoto(self.path, self.roi, self.photo))
        self.condition_cut_button.grid(column=0, row=0)
        self.condition_save_button = tk.Button(self.condition_button_frame, text="Save", font=BUTTON_FONT, command=lambda: savePhoto(self.path, self.photo))
        self.condition_save_button.grid(column=1, row=1)
        self.condition_button_frame.pack()

        # Sensor Pin
        self.sensor_frame = tk.Frame(self.windows, height=20)
        self.sensor_label = tk.Label(self.sensor_frame, text="IR sensor PIN  ", font=TITLE_NAME_FONT)
        self.sensor_label.grid(row=0, column=0)
        self.sensor_text = ttk.Combobox(self.sensor_frame, values=["Choose Sensor Pin","3", "5", "7", "8", "11", "12", "13", "15", "16", "18", "19", "21", "22",\
                        "23", "24", "26", "29", "31", "32", "33", "35", "36", "37", "38", "40"])
        self.sensor_text.current(0)
        self.sensor_text.grid(row=0, column=1)
        self.sensor_frame.pack()

        # other set
        self.other_frame = tk.Frame(self.windows, height=20)
        self.video_time_label = tk.Label(self.other_frame, text="Every video time(sec)", font=TITLE_NAME_FONT)
        self.video_time_label.grid(row=0, column=0)
        self.video_time_var = tk.StringVar()
        self.video_time_text = tk.Entry(self.other_frame, textvariable=self.video_time_var)
        self.video_time_text.grid(row=0, column=1)
        self.interval_time_label = tk.Label(self.other_frame, text="Delay time(sec)", font=TITLE_NAME_FONT)
        self.interval_time_label.grid(row=1, column=0)
        self.interval_time_var = tk.StringVar()
        self.interval_time_text = tk.Entry(self.other_frame, textvariable=self.interval_time_var)
        self.interval_time_text.grid(row=1, column=1)
        self.other_frame.pack()

        # output
        self.output_frame = tk.Frame(self.windows)
        self.check_basic_text = tk.StringVar()
        self.check_basic_label = tk.Label(self.output_frame, foreground="red", font=ALARM_FONT, textvariable=self.check_basic_text)
        self.check_basic_label.grid(row=0, column=0)
        self.check_pin_text = tk.StringVar()
        self.check_pin_label = tk.Label(self.output_frame, foreground="red", font=ALARM_FONT, textvariable=self.check_pin_text)
        self.check_pin_label.grid(row=1, column=0)
        self.check_time_text = tk.StringVar()
        self.check_time_label = tk.Label(self.output_frame, foreground="red", font=ALARM_FONT, textvariable=self.check_time_text)
        self.check_time_label.grid(row=2, column=0)
        self.output_frame.pack()

        user_choice_dict = {
            "Project_name": self.project_var,
            "FTP_IP" : self.FTP_var,
            "user": self.user_var,
            "password" : self.password_var,
            "path": self.path_text_var,
            "sensor": self.sensor_text,
            "video_time": self.video_time_var,
            "interval_time": self.interval_time_var,
            "method": self.method_value
        }

        self.produce_button = tk.Button(self.windows, text="Create", font=BUTTON_FONT, command=lambda : CheckUserInput(user_choice_dict, \
                                                                                                    alarmVars=[self.check_basic_text, self.check_pin_text, self.check_time_text]))
        self.produce_button.pack()
    
    def update_condition(self):
        
        if self.condition_value.get() == 0:
            image = Image.open("./basic_image/pi_GPIO.png").resize((480, 270))
            image = ImageTk.PhotoImage(image)
            self.photo = None
        else:
            frame = self.camera.get_frame()
            h, w = frame.shape[:2]
            self.photo = frame
            self.rate = 480 / w
            image = cv2.resize(frame, (int(self.rate*w), int(self.rate*h)))
            image = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.condition_image.configure(image=image)
        self.condition_image.image = image

        self.windows.after(self.delay, self.update_condition)
        

if __name__ == "__main__":
    GUI = collectImageGUI() 