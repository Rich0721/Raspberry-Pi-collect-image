import tkinter as tk
import tkinter.ttk as ttk

#from analyze.analyGUI import analyzeGUI
#from ExecuteResult.executeGUI import executeGUI
from collectData.image_collect_GUI import collectImageGUI
#from analyze.test_opencv import showGUI

###########################################
TITLE_NAME_FONT = ('Times', 12, 'bold')
BUTTON_FONT = ('Times', 10)
HINT_FONT = ("Times", 10)
###########################################



if  __name__ == "__main__":

    root = tk.Tk()
    root.title('I.Player')

    root.geometry('700x650')

    tab_main = ttk.Notebook()
    tab_main.pack(anchor=tk.NW)

    collect_gui = collectImageGUI(tab_main, os="pi")
    
    tab_main.add(collect_gui.getWindows(), text="Collect")
    '''
    analyze_gui = analyzeGUI(tab_main)
    
    tab_main.add(analyze_gui.getWindow(),text='Analysis')

    execute_gui = executeGUI(tab_main)
    tab_main.add(execute_gui.getWindows(), text="Execute")
    
    execute_gui.getWindows().after(1000, execute_gui.executeAnalysis)
    
    root.mainloop()
    '''
