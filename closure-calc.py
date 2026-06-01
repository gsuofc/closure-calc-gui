import math
import re
import tkinter as tk
import traceback
import turtle
import json
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import simpledialog
from datetime import datetime
from rows_controller import rows_controller
from version_checking import *
from closure_helper import *
from consts import *
from exporting import write_report_to_file
import threading
import webbrowser
import platform

import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def safe_evaluate(expression, enabled = True):
    if not enabled:
        return expression

    # Rather than passing any user input we see if 
    if not re.match(r"^[0-9+\-*/().\s]+$", expression):
        return expression # Possibly raise an error but at this point we only care for a value 
    
    try:
        #cleaned_expr = re.sub(r'\b0+(?=\d)', '', expression)
        evalued =  eval(expression)
        return evalued
    except:
        print("Error with eval: %s"%expression)
        return expression

class ClosureCalc(tk.Tk):
    def on_close(self):
        self.quit()
        self.destroy()

    def rebind_turtle_controls(self,canvas):
        canvas.bind("<MouseWheel>", self.zoom)
        canvas.bind("<ButtonPress-1>", self.start_pan)
        canvas.bind("<B1-Motion>", self.pan_move)

    def __init__(self):
        # Init the GUI
        super().__init__()

        build_text = get_version_number()
        if is_frozen():
            build_text+=" (running as executable)"
        else:
            build_text+=" (running as script)"

        self.tscreen = turtle.Screen()
        self.title("Plan Closure Calculator - %s"%build_text)
        self.geometry("1000x900")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        turtle_canvas = self.tscreen.getcanvas()
        turtle_root = turtle_canvas.winfo_toplevel()
        self.rebind_turtle_controls(turtle_canvas)
        turtle_root.protocol("WM_DELETE_WINDOW", self.on_close)
        turtle_root.title("Plan View - %s"%build_text)
        
        if platform.system() == "Windows":
            self.iconbitmap(resource_path("icon.ico"))
            turtle_root.iconbitmap(resource_path("icon.ico"))

        self.last_x = 0
        self.last_y = 0

        self.direct_points = []

        container = tk.Frame(self)
        container.pack(side="top",fill="both", expand=True)

        container2 = tk.Frame(self)
        container2.pack(side="bottom")

        save_button = tk.Button(container2,text="Save",command=self.save_closure)
        save_button.grid(row=0, column=0)

        load_button = tk.Button(container2,text="Load",command =self.load_closure)
        load_button.grid(row=0, column=1)

        load_button = tk.Button(container2,text="Clear",command =self.clear_closure)
        load_button.grid(row=0, column=2)
        
        load_button = tk.Button(container2,text="Generate Report",command =self.gen_report)
        load_button.grid(row=0, column=3)

        load_button = tk.Button(container2,text="Export as CSV",command =self.save_csv)
        load_button.grid(row=0, column=4)

        self.update_button = tk.Button(container2,text="Update Now!",command =self.update_redirect)
        #self.update_button.grid(row=0, column=4) Will be put in the update function! (make sure column is matched)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.currently_drawing = False

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        headers = [
            "Curve?", "Deg", "Min", "Sec", "Distance",
            "Radius", "Arc Length", "RB Deg", "RB Min", "RB Sec"
        ]
        for col, text in enumerate(headers):
            label = tk.Label(self.scrollable_frame, text=text, font=("Arial", 10, "bold"))
            label.grid(row=0, column=col, padx=5, pady=5)
        
        self.row_controller = rows_controller(self)

        for i in range(1,10):
            self.row_controller.add_row()

        self.closure_stats = []

        # Settings 
        self.settings_enable_eval = True

        self.turtle_main = turtle.Turtle()
        self.turtle_dots = turtle.Turtle()

        self.turtle_main.pensize(2)
        self.turtle_main.color("blue")
        self.turtle_main.speed(0)

        self.turtle_dots.pensize(5)
        self.turtle_dots.color("red")
        self.turtle_dots.speed(0)
        self.turtle_dots.penup()

        #Check for update
        threading.Thread(
            target=self._check_for_updates_thread,
            daemon=True
        ).start()
    
    def _check_for_updates_thread(self):
        if get_hash() is not None:
            try:
                if is_newer_version(get_hash()):
                    newest_version = get_latest_version_number()
                    self.after(
                        0,
                        lambda: self.update_is_detected(newest_version)
                    )
            except:
                print("Error checking for updates. Is Github Down, or are you connected to the internet?")
    def update_is_detected(self,newest_version):
        mb.showinfo(
            "Update Avalible", 
            f"There is a newer version ({newest_version}) available.\nYou currently have {get_hash()}.\nClick 'Update Now' or go to https://github.com/gsuofc/closure-calc-gui/releases"
        )
        self.update_button.grid(row=0, column=99)
        

    def update_redirect(self):
        webbrowser.open("https://github.com/gsuofc/closure-calc-gui/releases/latest")

    def add_row(self, index=None):
        self.row_controller.add_row(self, index)

    def gen_report(self):
        if self.currently_drawing:
            return
        
        if not self.closure_stats:
            return
        
        report_name = simpledialog.askstring("Name", "Enter the name of the closure for the report:", parent=self)

        if not report_name:
            report_name = "Untitled"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("TXT files", "*.txt"), ("All files", "*.*")],
            title="Save TXT File",
            initialfile=report_name
        )

        if file_path:
            write_report_to_file(file_path,report_name,self.closure_stats,self.direct_points)

    def save_csv(self):
        if self.currently_drawing:
            return
        
        easting = simpledialog.askfloat("Origin", "Easting of origin?", parent=self)

        if not easting:
            return

        northing = simpledialog.askfloat("Origin", "Northing of origin?", parent=self)
        
        if not northing: 
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV File"
        )

        if file_path:
            f = open(file_path,"w")
            index = 1
            for i in self.direct_points:
                f.write("%f,%f,0\n"%(i['y']+easting,i['x']+northing))
                index+=1
            f.close()
            print(f"Data saved to {file_path}")

    def save_closure(self):
        # Takes the values in all the inputs and saves them to a JSON file
        # The first step is to create an array and store all the rows as dicts
        all_data = []
        for row_widgets in self.rows:
            data = {
                "is_curve": row_widgets["curve"].get(),
                "deg": row_widgets["deg"].get(),
                "min": row_widgets["min"].get(),
                "sec": row_widgets["sec"].get(),
                "distance": row_widgets["distance"].get(),
                "radius": row_widgets["radius"].get(),
                "arc": row_widgets["arc"].get(),
                "rb_deg": row_widgets["rb_deg"].get(),
                "rb_min": row_widgets["rb_min"].get(),
                "rb_sec": row_widgets["rb_sec"].get()
            }
            all_data.append(data)
        
        # Now save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save JSON File"
        )

        header = {
            "program_name": FILE_PROG_MAGIC,
            "file_version": FILE_VERSION,
            "program_version": get_hash()
        }

        file = {
            "header": header,
            "data": all_data,
        }

        if file_path:
            with open(file_path, 'w') as f:
                json.dump(file, f, indent=4)
            print(f"Data saved to {file_path}")

    def clear_closure(self):
        answer = mb.askyesno("Clear all data?", "Do you want to clear all data? All unsaved changes will be lost.")
        if answer:
            self.row_controller.clear()
            for i in range(1,10):
                self.row_controller.add_row()
            self.row_controller.regrid_rows()
            self.compute_closure()

    def load_closure(self):
        # Takes a json file saved before and fill back in the data 
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open JSON File"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    file = json.load(f)
            except Exception as e:
                mb.showerror("Unable to open file", f"There was an error reading the file {file_path}.\nError: {e}")
                return
            
            data = []

            # Determine if the file is the legacy format
            try: 
                if isinstance(file, dict):
                    if "header" in file and "program_name" in file["header"]:
                        file_header = file["header"]["program_name"]
                        if file_header==FILE_PROG_MAGIC:
                            # At this point, it is safe to assume file is valid (idealy more validation happens but if the magic matches then it is super unlikely unless tampering occured)
                            file_ver = file["header"]["file_version"]
                            if file_ver < MIN_FILE_VERSION:
                                mb.showwarning("File version mismatch", "File may be too old to be supported by this software! \n(File version: %i, Min supported: %i)"%(file_ver,MIN_FILE_VERSION))
                            if file_ver > FILE_VERSION:
                                mb.showwarning("File version mismatch", "File may be too new to be supported by this software! \n(File version: %i, Max supported: %i)"%(file_ver,FILE_VERSION))

                            data = file["data"]
                        else:
                            raise ValueError("File header in file does not match expected file header")
                    else:
                        raise ValueError("File does not contain valid data to import. (JSON ROOT = Dict)")
                elif isinstance(file, list):
                    # Possibly a legacy file format
                    if len(file)>0 and isinstance(file[0], dict) and "is_curve" in file[0] and SUPPORT_LEGACY_FILE_FORMAT:
                        # Reason to believe its the legacy format, import it
                        print("%s is a legacy file format. Please note that support for this format is limited."%file_path)
                        data = file
                    else: 
                        raise ValueError("File does not contain valid data to import. (JSON ROOT = List)")
                else:
                    raise ValueError("File does not contain valid data to import. (JSON ROOT = Other)")
            except ValueError as e:
                mb.showerror("Unable to open file", f"There was an error opening the file {file_path}.\nError: {e}")
                return
            # Clear existing rows
            self.row_controller.clear()

            # Load new data
            try:
                for item in data:
                    self.row_controller.add_row()

                    row_widgets = self.row_controller.rows[-1]
                    row_widgets["curve"].set(item.get("is_curve", False))
                    row_widgets["deg"].insert(0, item.get("deg", ""))
                    row_widgets["min"].insert(0, item.get("min", ""))
                    row_widgets["sec"].insert(0, item.get("sec", ""))
                    row_widgets["distance"].insert(0, item.get("distance", ""))
                    row_widgets["radius"].insert(0, item.get("radius", ""))
                    row_widgets["arc"].insert(0, item.get("arc", ""))
                    row_widgets["rb_deg"].insert(0, item.get("rb_deg", ""))
                    row_widgets["rb_min"].insert(0, item.get("rb_min", ""))
                    row_widgets["rb_sec"].insert(0, item.get("rb_sec", ""))

                self.regrid_rows()
                self.compute_closure()
            except Exception as e:
                mb.showerror("Unable to open file", f"There was an error processing the file {file_path}.\nError: {e}")
                traceback.print_exc()

    def _on_mousewheel(self, event):
        # On Windows and Mac, event.delta is multiples of 120
        self.scrollable_frame.update_idletasks()  # Make sure layout updated
        self.scrollable_frame.master.yview_scroll(int(-1*(event.delta/120)), "units")

    def insert_row_at(self, index):
        self.add_row(index)
        
    def remove_row_at(self, index):
        if index < len(self.rows) - 2:
            row_widgets = self.rows.pop(index)
            for widget in row_widgets.values():
                if isinstance(widget, (tk.Entry, tk.Checkbutton, tk.Button)):
                    widget.destroy()
        self.regrid_rows()
        self.compute_closure()

    def regrid_rows(self):
        #TODO: REMOVE
        self.row_controller.regrid_rows()

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def compute_closure(self):
        if self.currently_drawing:
            return
        self.currently_drawing = True
        self.distances = []
        self.direct_points = []
        x=0
        y=0
        prevx=0
        prevy=0
        bearing=0
        distance = 0

        radius = 0

        minx = -5
        miny = -5
        maxx = 5
        maxy = 5
        
        # Reset turtle
        turtle.clearscreen()
        self.turtle_main.clear()
        self.turtle_dots.clear()
        self.turtle_main.penup()
        self.turtle_main.goto(0, 0)
        self.turtle_main.setheading(0)
        self.turtle_main.pendown()
        self.turtle_dots.penup()

        t = self.turtle_main
        t2 = self.turtle_dots #TODO: refactor this properly
        t.pensize(2)
        t.color("blue")
        t.speed(0)

        t2.pensize(5)
        t2.color("red")
        t2.speed(0)

        self.tscreen.tracer(0)  # Turn off automatic screen updates

        for row_widgets in self.row_controller.rows:
            line_segment = {}
            curve_segment = {}

            is_curve = row_widgets["curve"].get()
            # Calculation depends on if the segment is a curve or a straight line
            if is_curve:
                d = row_widgets["deg"].get()
                m = row_widgets["min"].get()
                s = row_widgets["sec"].get()
                r = safe_evaluate(row_widgets["radius"].get(),self.settings_enable_eval)
                a = safe_evaluate(row_widgets["arc"].get(),self.settings_enable_eval)

                rd = row_widgets["rb_deg"].get()
                rm = row_widgets["rb_min"].get()
                rs = row_widgets["rb_sec"].get()

                curve_segment["rad-bear"] = False

                if self.is_number(rd) and self.is_number(rm) and self.is_number(rs):
                    # If a radial bearing is given, change the current bearing to that (otherwise use the last bearing as the starting bearing)
                    b = compute_dd_from_dms(float(rd),float(rm),float(rs))
                    b-=90
                    bearing = math.radians(b)
                    #Save radial bearing to file
                    curve_segment["rad-bear"] = True
                    curve_segment["rad-d"] = float(rd)
                    curve_segment["rad-m"] = float(rm)
                    curve_segment["rad-s"] = float(rs)

                if self.is_number(r):
                    radius = float(r)

                if self.is_number(d) and self.is_number(m) and self.is_number(s) and radius!=0:
                    # If interior angle is given, compute the curve from that
                    dd = compute_dd_from_dms(float(d),float(m),float(s))
                    if radius<0:
                        dd*=-1

                    (dx,dy,bearing_new) = compute_dxdy_from_curve_delta(bearing,math.radians(dd),radius)
                    x+=dx
                    y+=dy

                    t.seth((90-math.degrees(bearing))%360)
                    t.circle(radius,abs(dd))

                    bearing = bearing_new
                    distance+=abs(radius*math.radians(dd))

                    curve_segment["radius"] = radius
                    curve_segment["arc"] = radius*math.radians(dd)
                elif radius!=0 and self.is_number(a):
                    #if the arc length is given, convert to interior angle and then compute from that
                    rad = float(a)/radius
                    (dx,dy,bearing_new) = compute_dxdy_from_curve_delta(bearing,rad,radius)
                    x+=dx
                    y+=dy

                    t.seth((90-math.degrees(bearing))%360)
                    t.circle(radius,abs(math.degrees(rad)))

                    bearing = bearing_new
                    distance+=abs(float(a))

                    curve_segment["radius"] = radius
                    curve_segment["arc"] = float(a)
                
                # Save bearing after curve for file saving/drawing
                b_degrees = bearing*180/math.pi
                (b_d, b_m, b_s) = compute_dms_from_dd(b_degrees)
                curve_segment["bearing-d"] = float(b_d)
                curve_segment["bearing-m"] = float(b_m)
                curve_segment["bearing-s"] = float(b_s)

            else:
                # A straight line just uses the direct problem
                d = row_widgets["deg"].get()
                m = row_widgets["min"].get()
                s = row_widgets["sec"].get()
                di = safe_evaluate(row_widgets["distance"].get(),self.settings_enable_eval)

                # Reset the curve radius
                radius = 0

                if self.is_number(di):
                    # If a new bearing is given, use that as the bearing. Otherwise reuse the last bearing
                    if self.is_number(d) and self.is_number(m) and self.is_number(s): 
                        b = compute_dd_from_dms(float(d),float(m),float(s))
                        bearing = math.radians(b)
                    
                    (dx,dy,bearing_new) = compute_dxdy_from_straightline(bearing,float(di))

                    t.seth((90-math.degrees(bearing_new))%360)
                    t.forward(float(di))

                    x+=dx
                    y+=dy
                    bearing = bearing_new

                    if float(di)<0:
                        # If a distance is negative, treat that as 180 in the other way
                        bearing+=math.radians(180)

                    distance+=abs(float(di))

                    # Save distance and bearing to file to save/display
                    line_segment["distance"] = abs(float(di))
                    b_degrees = bearing*180/math.pi
                    (b_d, b_m, b_s) = compute_dms_from_dd(b_degrees)
                    line_segment["bearing-d"] = float(b_d)
                    line_segment["bearing-m"] = float(b_m)
                    line_segment["bearing-s"] = float(b_s)

                        
            # Update bounds of screen
            if x < minx:
                minx = x
            if y < miny:
                miny = y
            if x > maxx:
                maxx = x
            if y > maxy:
                maxy = y

            # Compute ranges
            xrange = maxx - minx
            yrange = maxy - miny
            padding = 1.4

            # Use the largest of the two ranges for a square view
            max_range = max(xrange, yrange) * padding

            # Compute midpoints
            xmid = (minx + maxx) / 2
            ymid = (miny + maxy) / 2

            # Swap x and y deliberately for coordinate system
            # y becomes horizontal (left/right), x becomes vertical (bottom/top)
            self.tscreen.setworldcoordinates(
                ymid - max_range / 2,  # left (x-axis, actually y)
                xmid - max_range / 2,  # bottom (y-axis, actually x)
                ymid + max_range / 2,  # right
                xmid + max_range / 2   # top
            )
            t2.penup()
            t2.goto(y,x)
            t2.dot(10,"red")

            while bearing<0:
                bearing+=math.radians(360)

            if prevx!=x or prevy!=y:
                coords = {
                    'x': x,
                    'y': y,
                    'is_curve': is_curve
                }
                if is_curve:
                    coords["curve_segment"] = curve_segment
                else:
                    coords["line_segment"] = line_segment
                self.direct_points.append(coords)

            prevx=x
            prevy=y

        dist = math.sqrt(x**2+y**2)
        # dist = final displacement, distance = sum of lengths of the segments

        closure = float('inf')      
        # To avoid a /0 error, only divide if dist is not equal to 0. (closure is listed as 1/n and a perfect closure means 1/0)
        if dist!=0:
            closure = distance/dist

        while bearing>2*math.pi:
            bearing-=2*math.pi

        b_degrees = bearing*180/math.pi

        (b_d, b_m, b_s) = compute_dms_from_dd(b_degrees)

        t.color("black")
        t.write("Closure: 1/%.0f \nd:%.3f di: %.3f\n(x: %.3f, y: %.3f)\nBearing: %d-%d-%.3f"%(closure,dist,distance,x,y,b_d,b_m,b_s))

        self.closure_stats = {
            "closure":closure,
            "displacement":dist,
            "distance":distance,
            "x":x,
            "y":y,
        }

        self.tscreen.update()  # Turn off automatic screen updates

        self.rebind_turtle_controls(self.tscreen.getcanvas())

        self.currently_drawing = False

    def zoom(self, event):
        canvas = self.tscreen.getcanvas()
        scale_factor = 1.1 if event.delta > 0 else 0.9
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        canvas.scale("all",x,y,scale_factor,scale_factor)

    def start_pan(self,event):
        self.last_x =  event.x
        self.last_y = event.y

        return "break" # Do this to still allow focus to be set

    def pan_move(self,event):
        canvas = self.tscreen.getcanvas()

        x = event.x
        y = event.y

        dx = x - self.last_x
        dy = y - self.last_y

        canvas.move("all", dx, dy)

        self.last_x = x
        self.last_y = y

if __name__ == "__main__":
    app = ClosureCalc()
    app.mainloop()
