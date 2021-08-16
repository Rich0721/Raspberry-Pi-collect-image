from tkinter import messagebox as msg
from PIL import ImageTk, Image
from tkinter import filedialog
import re
import json

#################################################
IP_RELU = "^10.(96|97).+((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.)(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
PI_USED_PIN = [3, 5, 7, 8, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, \
                32, 33, 35, 36, 37, 38, 40]
#################################################

def limitInputDigital(P):
    if str.isdigit(P) or P == '':
        return True
    else:
        return False


def OpenImage(textvar, image_label):
    
    filename = filedialog.askopenfilename(filetypes=[("jpeg files","*.jpg"), ("png files", "*.png"),\
                                         ("bmp files", "*.bmp"), ("All image files", "*.jpg *.jpeg *.png *.gif *.bmp")])
    if len(filename) > 0:
        textvar.set(filename)
        image = Image.open(filename).resize((400, 300))
        image = ImageTk.PhotoImage(image)
        image_label.configure(image=image)
        image_label.image = image


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
        if stringVars["method"].get() == 1:
            show_text += "Method:Image\n"
        elif stringVars["method"].get() == 2:
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

    if stringVars["method"].get() == 1:
        data["method"] = "image"
    elif stringVars["method"].get() == 2:
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