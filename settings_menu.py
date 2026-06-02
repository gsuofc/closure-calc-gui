import json
from pathlib import Path
import platform
import tkinter as tk

from consts import get_hash, get_version_number, resource_path

SETTINGS_FILE = Path.home() / ".closure-calc-config.json"

SETTINGS_OPTIONS = {
    "enable_math_eval": {"label":"Enable Math Eval","default_value":True}
}

class Settings_Menu():
    def __init__(self,app=None):
        self.app = app
        self.window = None
        self.check_vars = {}

        self.configure_settings()

    def configure_settings(self):
        self.settings = {}
        # TODO: Load from settings config file
        try:
            with open(SETTINGS_FILE, "r") as file:
                loaded_settings = json.load(file)
                self.settings = loaded_settings["settings"]
                print("Loaded settings file")
        except:
            print("Cannot open settings file. Default options loading...")
            # Init with default options
            for index, key in enumerate(SETTINGS_OPTIONS):
                self.settings[key] = SETTINGS_OPTIONS[key]["default_value"]

        self.save_settings()

    def save_settings(self):
        for index, key in enumerate(self.settings):
            if key in self.check_vars:
                check = self.check_vars[key]
                choice = check.get()
                self.settings[key] = choice

        settings_json = {
            "last_opened_version": get_version_number(),
            "last_opened_githash": get_hash(),
            "settings": self.settings
        }
        
        print("Saving settings to %s"%SETTINGS_FILE)
        with open(SETTINGS_FILE, "w") as file:
            json.dump(settings_json, file, indent=4)

    def gen_gui(self):
        if self.window:
            self.window.withdraw()
        self.window = tk.Toplevel(self.app)
        self.window.title("Settings")
        self.window.minsize(width=350,height=500)
        self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)

        if platform.system() == "Windows":
            self.window.iconbitmap(resource_path("icon.ico"))

        settings_frame = tk.Frame(self.window)
        settings_frame.pack(side="top",fill="both", expand=True)

        bottom_bar = tk.Frame(self.window)
        bottom_bar.pack(side="bottom")

        save_button = tk.Button(bottom_bar,text="Cancel",command=self.cancel_settings)
        save_button.grid(row=0, column=2)

        save_button = tk.Button(bottom_bar,text="Apply",command=self.apply_settings)
        save_button.grid(row=0, column=1)

        save_button = tk.Button(bottom_bar,text="Ok",command=self.ok_settings)
        save_button.grid(row=0, column=0)

        settings_frame.grid_columnconfigure(1, minsize=300)

        for index, key in enumerate(self.settings):
            label_text = key
            if key in SETTINGS_OPTIONS:
                if "label" in SETTINGS_OPTIONS[key]:
                    label_text = SETTINGS_OPTIONS[key]["label"] 
            label = tk.Label(settings_frame, text=label_text,font=("Arial", 10, "bold"))
            curve_var = tk.BooleanVar(value=self.settings[key])
            self.check_vars[key] = curve_var
            curve_check = tk.Checkbutton(
                settings_frame,
                variable=curve_var,
            )
            label.grid(row=index, column=1)
            curve_check.grid(row=index, column=2)

    def show_settings_menu(self):
        self.gen_gui()
        self.window.deiconify() # FOR DEBUG - REMOVE
        self.window.attributes('-topmost', True)
        self.window.focus_force()

    def cancel_settings(self):
        self.window.withdraw()

    def apply_settings(self):
        self.save_settings()

    def ok_settings(self):
        self.save_settings()
        self.cancel_settings()

    def get_settings_option(self,key):
        return self.settings[key]