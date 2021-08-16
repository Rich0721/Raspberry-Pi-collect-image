import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from GUI_commond import OpenImage, limitInputDigital, CheckUserInput, hardware_commond, software_commond

###########################################
TITLE_NAME_FONT = ('Times', 16, 'bold')
BUTTON_FONT = ('Times', 16)
ALARM_FONT = ("Times", 16,  "bold")
IMAGE_WIDTH = 0
IMAGE_HEIGHT = 0
###########################################


def setBasicLabel(windows, vcmd):

    # Set project, FTP, user and password's label and text
    basic_set_frame = tk.Frame(windows, width=100, height=200)
    project_label = tk.Label(basic_set_frame, text="Project name", font=TITLE_NAME_FONT)
    project_label.grid(column=0, row=0)
    project_var = tk.StringVar()
    project_text = tk.Entry(basic_set_frame, textvariable=project_var)
    project_text.grid(column=1, row=0)
    FTP_label = tk.Label(basic_set_frame, text="FTP server IP", font=TITLE_NAME_FONT)
    FTP_label.grid(column=0, row=1)
    FTP_var = tk.StringVar()
    FTP_text = tk.Entry(basic_set_frame, textvariable=FTP_var)
    FTP_text.grid(column=1, row=1)
    user_label = tk.Label(basic_set_frame, text="user", font=TITLE_NAME_FONT)
    user_label.grid(column=0, row=2)
    user_var = tk.StringVar()
    user_text = tk.Entry(basic_set_frame, textvariable=user_var)
    user_text.grid(column=1, row=2)
    password_label = tk.Label(basic_set_frame, text="password", font=TITLE_NAME_FONT)
    password_label.grid(column=0, row=3)
    password_var = tk.StringVar()
    password_text = tk.Entry(basic_set_frame, textvariable=password_var)
    password_text.grid(column=1, row=3)
    basic_set_frame.pack()

    # Set collect image of method
    method_value = tk.IntVar()
    #method_value.set(1)
    method_frame = tk.Frame(windows, width=100, height=50)
    method_label = tk.Label(method_frame, text="Collected method" , font=TITLE_NAME_FONT)
    method_label.grid(column=0, row=0)
    method_image_btn = tk.Radiobutton(method_frame, text="image", variable=method_value, value=0, font=BUTTON_FONT)
    method_image_btn.grid(column=1, row=0)
    method_video_btn = tk.Radiobutton(method_frame, text='video', variable=method_value, value=1, font=BUTTON_FONT)
    method_video_btn.grid(column=2, row=0)
    method_frame.pack()

    # Set collect image condition
    condition_value = tk.IntVar()
    path_text_var = tk.StringVar()
    condition_frame = tk.Frame(windows, width=100, height=250)
    condition_label = tk.Label(condition_frame, text="Trigger Image", font=TITLE_NAME_FONT)
    condition_label.grid(column=0, row=0)
    condition_hardware = tk.Radiobutton(condition_frame, text="hardware", variable=condition_value, value=0, font=BUTTON_FONT, command=lambda:hardware_commond(condition_image))
    condition_hardware.grid(column=1, row=0)
    condition_software = tk.Radiobutton(condition_frame, text="software", variable=condition_value, value=1, font=BUTTON_FONT, command=lambda:software_commond(condition_image, IMAGE_WIDTH, IMAGE_HEIGHT))
    condition_software.grid(column=2, row=0)
    condition_frame.pack()
    print("{}, {}".format(IMAGE_WIDTH, IMAGE_HEIGHT))
    # condition real image
    condition_image_frame = tk.Frame(windows, width=480, height=320)
    #condition_image_path = tk.Label(condition_frame, textvariable=path_text_var, font=BUTTON_FONT)
    #condition_image_path.grid(row=1, columnspan=2)
    condition_image = tk.Label(condition_image_frame)
    hardware_commond(condition_image)
    condition_image.pack()
    condition_image_frame.pack()

    # Sensor Pin
    sensor_frame = tk.Frame(windows, height=20)
    sensor_label = tk.Label(sensor_frame, text="IR sensor PIN  ", font=TITLE_NAME_FONT)
    sensor_label.grid(row=0, column=0)
    sensor_text = ttk.Combobox(sensor_frame, values=["Choose Sensor Pin","3", "5", "7", "8", "11", "12", "13", "15", "16", "18", "19", "21", "22",\
                    "23", "24", "26", "29", "31", "32", "33", "35", "36", "37", "38", "40"])
    sensor_text.current(0)
    sensor_text.grid(row=0, column=1)
    sensor_frame.pack()

    # other set
    other_frame = tk.Frame(windows, height=20)
    video_time_label = tk.Label(other_frame, text="Every video time(sec)", font=TITLE_NAME_FONT)
    video_time_label.grid(row=0, column=0)
    video_time_var = tk.StringVar()
    video_time_text = tk.Entry(other_frame, textvariable=video_time_var)
    video_time_text.grid(row=0, column=1)
    interval_time_label = tk.Label(other_frame, text="Delay time(sec)", font=TITLE_NAME_FONT)
    interval_time_label.grid(row=1, column=0)
    interval_time_var = tk.StringVar()
    interval_time_text = tk.Entry(other_frame, textvariable=interval_time_var)
    interval_time_text.grid(row=1, column=1)
    other_frame.pack()

    # output
    output_frame = tk.Frame(windows)
    check_basic_text = tk.StringVar()
    check_basic_label = tk.Label(output_frame, foreground="red", font=ALARM_FONT, textvariable=check_basic_text)
    check_basic_label.grid(row=0, column=0)
    check_pin_text = tk.StringVar()
    check_pin_label = tk.Label(output_frame, foreground="red", font=ALARM_FONT, textvariable=check_pin_text)
    check_pin_label.grid(row=1, column=0)
    check_time_text = tk.StringVar()
    check_time_label = tk.Label(output_frame, foreground="red", font=ALARM_FONT, textvariable=check_time_text)
    check_time_label.grid(row=2, column=0)
    output_frame.pack()

    user_choice_dict = {
        "Project_name": project_var,
        "FTP_IP" : FTP_var,
        "user": user_var,
        "password" : password_var,
        "path": path_text_var,
        "sensor": sensor_text,
        "video_time": video_time_var,
        "interval_time": interval_time_var,
        "method": method_value
    }

    produce_button = tk.Button(windows, text="Create", font=BUTTON_FONT, command=lambda : CheckUserInput(user_choice_dict, \
                                                                                                alarmVars=[check_basic_text, check_pin_text, check_time_text]))
    produce_button.pack()

    return windows    


if __name__ == "__main__":
    windows = tk.Tk()
    windows.title("AUO L7B影像蒐集")
    windows.geometry("600x800")
    vcmd = windows.register(limitInputDigital, "%P")
    windows = setBasicLabel(windows, vcmd)
    windows.mainloop()