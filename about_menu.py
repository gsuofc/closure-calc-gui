import tkinter as tk
from consts import *
import platform

INFO_FONT = ("Arial", 10, "bold")
INFO_SUBFONT = ("Arial", 10)

INFO_SUBITEMS = [
                    f"Running via PyInstaller: {is_frozen()}",
                    f"Build Date: {build_date()}",
                    f"Build Method: {build_method()}",
                    f"File Version: {FILE_VERSION}",
                    f"Git Hash: {get_hash()}",
                ]

class About_Window():
    def __init__(self,app=None):
        self.app = app
        self.window = None
        self.check_vars = {}

    def gen_gui(self):
        self.window = tk.Toplevel(self.app)
        self.window.title("About")
        self.window.minsize(width=350,height=500)
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.window.resizable(False, False)

        if platform.system() == "Windows":
            self.window.iconbitmap(resource_path("icon.ico"))

        # HEADER 
        title_container = tk.Frame(self.window)
        title_container.grid(row=0, column=0)

        img = tk.PhotoImage(file=resource_path("icon.png")).zoom(2, 2)
        logo_label = tk.Label(title_container,image=img)
        logo_label.image = img
        logo_label.grid(row=0, column=0,padx=20, pady=10)

        title_label = tk.Label(title_container,text="Closure Calc GUI", font=("Arial", 15, "bold"))
        title_label.grid(row=0, column=1)

        # VERSION

        title_label = tk.Label(self.window,text=f"Version: {get_version_number()}", font=INFO_FONT)
        title_label.grid(row=1, column=0)
    
        # AUTHORS

        author_containers = tk.Frame(self.window)
        author_containers.grid(row=2, column=0)

        title_label = tk.Label(author_containers,text=f"Program Written By", font=INFO_FONT)
        title_label.grid(row=0, column=0,padx=20)
        
        index_auth = 0
        for author in AUTHORS:
            title_label = tk.Label(author_containers,text=author, font=INFO_FONT)
            title_label.grid(row=index_auth, column=1,padx=20)
            index_auth+=1

        for index, value in enumerate(INFO_SUBITEMS): 
            label = tk.Label(self.window,text=value)
            label.grid(row=index+3, column=0)



    def show_about(self):
        self.gen_gui()
        self.window.grab_set() 
        self.window.focus_force()