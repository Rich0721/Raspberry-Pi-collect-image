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
###########################################

def goToGUI(root, choice=0):
    root.destroy()
    if choice == 0:
        collect_gui = collectImageGUI(os=OS)
        collect_gui.__del__()
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

    button_frame = tk.Frame(root)
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

    logo_image = Image.open("./IPlayer_logo.png")
    w, h = logo_image.size
    logo_image.resize((w//4, h//4))
    logo_image = ImageTk.PhotoImage(logo_image)
    image_label = tk.Label(root, image=logo_image)
    image_label.place(x=50, y=100)

    root.mainloop()

    

if  __name__ == "__main__":

    main_GUI()
    
    
    '''
    root = tk.Tk()
    root.title('I.Player')

    root.geometry('700x650')

    tab_main = ttk.Notebook()
    tab_main.pack(anchor=tk.NW)

    collect_gui = collectImageGUI(tab_main, os="windows")
    
    tab_main.add(collect_gui.getWindows(), text="Collect")
    
    analyze_gui = analyzeGUI(tab_main)
    
    tab_main.add(analyze_gui.getWindow(),text='Analysis')

    visualization_gui = visualizationGUI(tab_main)
    tab_main.add(visualization_gui.getWindows(), text='Visualization')

    execute_gui = executeGUI(tab_main)
    tab_main.add(execute_gui.getWindows(), text="Execute")
    
    execute_gui.getWindows().after(1000, execute_gui.executeAnalysis)
    
    root.mainloop()
    '''
