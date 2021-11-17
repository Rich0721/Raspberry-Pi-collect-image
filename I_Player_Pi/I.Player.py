import tkinter as tk
from PIL import Image, ImageTk
from collectData.image_collect_GUI import collectImageGUI


###########################################
TITLE_NAME_FONT = ('Times', 12, 'bold')
BUTTON_FONT = ('Times', 10)
HINT_FONT = ("Times", 10)
OS = "pi"
if OS == "windows":
    from analyze.analyGUI import analyzeGUI
    from ExecuteResult.executeGUI import executeGUI
    from mergeCSV.mergeGUI import mergeGUI
BACKGROUND_COLOR = "#D6CBC7"
###########################################

def goToGUI(root, choice=0):
    root.destroy()
    if choice == 0:
        collect_gui = collectImageGUI(os_type=OS)
    elif choice == 1:
        analyze_gui = analyzeGUI()
    elif choice == 2:
        execute_gui = executeGUI()
    elif choice == 3:
        merge_gui = mergeGUI()
    main_GUI()
    
    

def main_GUI():

    root = tk.Tk()
    root.title("I.Player")
    root.geometry('200x200')
    root.resizable(False, False)
    background_image = Image.open("./logo_images/Main_background.png")
    photo = ImageTk.PhotoImage(background_image)
    background_canvas = tk.Canvas(root, width=200, height=200)
    background_canvas.background = photo
    background_canvas.create_image(100, 100 , image=photo)
    background_canvas.pack()

    button_frame = tk.Frame(root, background=BACKGROUND_COLOR)
    collect_button = tk.Button(button_frame, text="Collect", font=BUTTON_FONT, command=lambda:goToGUI(root, choice=0))
    collect_button.grid(row=0, column=0, padx=5, pady=5)
    if OS == "windows":
        analyze_button = tk.Button(button_frame, text="Analyze", font=BUTTON_FONT,  command=lambda:goToGUI(root, choice=1))
        analyze_button.grid(row=0, column=1, padx=5, pady=5)
        execute_button = tk.Button(button_frame, text="Execute", font=BUTTON_FONT,  command=lambda:goToGUI(root, choice=2))
        execute_button.grid(row=1, column=0, padx=5, pady=5)
        merge_button = tk.Button(button_frame, text="Merge CSV", font=BUTTON_FONT, command=lambda:goToGUI(root, choice=3))
        merge_button.grid(row=1, column=1, padx=5, pady=5)
    button_frame.pack()
    background_canvas.create_window(100, 50, window=button_frame)

    root.mainloop()

    

if  __name__ == "__main__":

    main_GUI()
    