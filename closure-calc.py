import math
import tkinter as tk
import turtle
import json
from tkinter import filedialog
from tkinter import messagebox as mb
from functools import partial

class ClosureCalc(tk.Tk):
    def on_close(self):
        self.quit()
        self.destroy()

    def __init__(self):
        # Init the GUI
        super().__init__()
        self.tscreen = turtle.Screen()
        self.title("Plan Closure Calculator")
        self.geometry("800x900")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        container = tk.Frame(self)
        container.pack(side="top",fill="both", expand=True)

        container2 = tk.Frame(self)
        container2.pack(side="bottom")

        save_button = tk.Button(container2,text="Save",command=self.save_closure)
        save_button.pack(side="left")

        load_button = tk.Button(container2,text="Load",command =self.load_closure)
        load_button.pack(side="right")

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

        self.rows = []
        for i in range(1,10):
            self.add_row()

    def add_row(self, index=None):
        if index is None:
            index = len(self.rows)

        row_widgets = {}

        curve_var = tk.BooleanVar()
        curve_check = tk.Checkbutton(
            self.scrollable_frame,
            variable=curve_var,
            command=self.regrid_rows
        )
        row_widgets["curve"] = curve_var
        row_widgets["check"] = curve_check

        fields = [
            "deg", "min", "sec",
            "distance", "radius", "arc",
            "rb_deg", "rb_min", "rb_sec"
        ]


        for field in fields:
            row_widgets[field] = tk.Entry(self.scrollable_frame, width=10)
            row_widgets[field].bind("<FocusOut>", lambda e, r=row_widgets: self.on_entry_edit(r))
            row_widgets[field].bind("<Return>", partial(self._handle_return, index, field))
            row_widgets[field].bind("<Shift-Return>", partial(self._handle_shift_return, index, field))

        def make_insert_callback(index):
            return lambda: self.insert_row_at(index)

        def make_remove_callback(index):
            return lambda: self.remove_row_at(index)

        row_widgets["insert_btn"] = tk.Button(
            self.scrollable_frame,
            text="+",
            width=2,
            command=make_insert_callback(index)
        )

        row_widgets["remove_btn"] = tk.Button(
            self.scrollable_frame,
            text="-",
            width=2,
            command=make_remove_callback(index)
        )

        self.rows.insert(index, row_widgets)
        self.regrid_rows()

    def _handle_return(self, index, field, event):
        self.focus_next_row_field(index, field)

    def _handle_shift_return(self, index, field, event):
        self.focus_prev_row_field(index, field)

    def focus_next_row_field(self, index, field):
        next_index = index + 1
        if next_index < len(self.rows):
            next_row = self.rows[next_index]
            if field in next_row and next_row[field].winfo_viewable():
                next_widget = next_row[field]
                next_widget.focus_set()
            else:
                next_widget = next_row["deg"]
                next_widget.focus_set()

    def focus_prev_row_field(self, index, field):
        prev_index = index - 1
        if prev_index > 0:
            prev_row = self.rows[prev_index]
            if field in prev_row and prev_row[field].winfo_viewable():
                next_widget = prev_row[field]
                next_widget.focus_set()
            else:
                next_widget = prev_row["deg"]
                next_widget.focus_set()

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

        if file_path:
            with open(file_path, 'w') as f:
                json.dump(all_data, f, indent=4)
            print(f"Data saved to {file_path}")

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
                    data = json.load(f)
            except Exception as e:
                mb.showerror("Unable to open file", f"There was an error reading the file {file_path}.\nError: {e}")
                return

            # Clear existing rows
            for row in self.rows:
                for widget in row.values():
                    if isinstance(widget, tk.Entry):
                        widget.destroy()
                    elif isinstance(widget, tk.Checkbutton) or isinstance(widget, tk.Button):
                        widget.destroy()
            self.rows.clear()

            # Load new data
            for item in data:
                self.add_row()

                row_widgets = self.rows[-1]
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
            self.compute_closure()


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
        for i, row_widgets in enumerate(self.rows, start=1):
            row_widgets["check"].grid(row=i, column=0, padx=5, pady=2)
            row_widgets["deg"].grid(row=i, column=1, padx=3, pady=2)
            row_widgets["min"].grid(row=i, column=2, padx=3, pady=2)
            row_widgets["sec"].grid(row=i, column=3, padx=3, pady=2)

            # Field visibility depending on curve checkbox
            if row_widgets["curve"].get():
                row_widgets["distance"].grid_remove()
                row_widgets["radius"].grid(row=i, column=5, padx=3, pady=2)
                row_widgets["arc"].grid(row=i, column=6, padx=3, pady=2)
                row_widgets["rb_deg"].grid(row=i, column=7, padx=3, pady=2)
                row_widgets["rb_min"].grid(row=i, column=8, padx=3, pady=2)
                row_widgets["rb_sec"].grid(row=i, column=9, padx=3, pady=2)
            else:
                row_widgets["distance"].grid(row=i, column=4, padx=3, pady=2)
                row_widgets["radius"].grid_remove()
                row_widgets["arc"].grid_remove()
                row_widgets["rb_deg"].grid_remove()
                row_widgets["rb_min"].grid_remove()
                row_widgets["rb_sec"].grid_remove()

            # Grid the Insert Row button
            row_widgets["insert_btn"].grid(row=i, column=10, padx=3, pady=2)
            row_widgets["remove_btn"].grid(row=i, column=11, padx=3, pady=2)

            row_widgets["insert_btn"].configure(command=lambda idx=i-1: self.insert_row_at(idx))
            row_widgets["remove_btn"].configure(command=lambda idx=i-1: self.remove_row_at(idx))

    def toggle_fields(self, row_widgets):
        # When the "curve" checkbox is changed, change which boxes are visible
        is_curve = row_widgets["curve"].get()

        if is_curve:
            row_widgets["distance"].grid_remove()
            row_widgets["radius"].grid()
            row_widgets["arc"].grid()
            row_widgets["rb_deg"].grid()
            row_widgets["rb_min"].grid()
            row_widgets["rb_sec"].grid()
        else:
            row_widgets["distance"].grid()
            row_widgets["radius"].grid_remove()
            row_widgets["arc"].grid_remove()
            row_widgets["rb_deg"].grid_remove()
            row_widgets["rb_min"].grid_remove()
            row_widgets["rb_sec"].grid_remove()

    def on_entry_edit(self, row_widgets):
        if row_widgets == self.rows[-1] or row_widgets == self.rows[-2]:
            # If any field has data, create a new row
            for key in [
                "deg", "min", "sec", "distance",
                "radius", "arc", "rb_deg", "rb_min", "rb_sec"
            ]:
                val = row_widgets[key].get()
                if val.strip():
                    for i in range(1,10):
                        self.add_row()
                    break
        self.compute_closure()

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
        x=0
        y=0
        bearing=0
        distance = 0

        radius = 0

        minx = -5
        miny = -5
        maxx = 5
        maxy = 5
        
        # Reset turtle
        turtle.clearscreen()
        t = turtle.Turtle()
        t2 = turtle.Turtle()
        t.pensize(2)
        t.color("blue")
        t.speed(0)

        t2.pensize(5)
        t2.color("red")
        t2.speed(0)

        self.tscreen.tracer(0)  # Turn off automatic screen updates

        for row_widgets in self.rows:
            is_curve = row_widgets["curve"].get()
            # Calculation depends on if the segment is a curve or a straight line
            if is_curve:
                d = row_widgets["deg"].get()
                m = row_widgets["min"].get()
                s = row_widgets["sec"].get()
                r = row_widgets["radius"].get()
                a = row_widgets["arc"].get()

                rd = row_widgets["rb_deg"].get()
                rm = row_widgets["rb_min"].get()
                rs = row_widgets["rb_sec"].get()

                if self.is_number(rd) and self.is_number(rm) and self.is_number(rs):
                    # If a radial bearing is given, change the current bearing to that (otherwise use the last bearing as the starting bearing)
                    b = float(rd)
                    b += float(rm)/60
                    b += float(rs)/(60*60)
                    b-=90
                    bearing = math.radians(b)

                if self.is_number(r):
                    radius = float(r)

                if self.is_number(d) and self.is_number(m) and self.is_number(s) and radius!=0:
                    # If interior angle is given, compute the curve from that
                    dd = float(d)
                    dd += float(m)/60
                    dd += float(s)/(60*60)
                    if radius<0:
                        dd*=-1

                    (dx,dy,bearing_new) = self.compute_dxdy_from_curve_delta(bearing,math.radians(dd),radius)
                    x+=dx
                    y+=dy

                    t.seth((90-math.degrees(bearing))%360)
                    t.circle(radius,abs(dd))

                    bearing = bearing_new
                    distance+=abs(radius*math.radians(dd))
                elif radius!=0 and self.is_number(a):
                    #if the arc length is given, convert to interior angle and then compute from that
                    rad = float(a)/radius
                    (dx,dy,bearing_new) = self.compute_dxdy_from_curve_delta(bearing,rad,radius)
                    x+=dx
                    y+=dy

                    t.seth((90-math.degrees(bearing))%360)
                    t.circle(radius,abs(math.degrees(rad)))

                    bearing = bearing_new
                    distance+=abs(float(a))

            else:
                # A straight line just uses the direct problem
                d = row_widgets["deg"].get()
                m = row_widgets["min"].get()
                s = row_widgets["sec"].get()
                di = row_widgets["distance"].get()

                # Reset the curve radius
                radius = 0

                if self.is_number(di):
                    # If a new bearing is given, use that as the bearing. Otherwise reuse the last bearing
                    if self.is_number(d) and self.is_number(m) and self.is_number(s): 
                        b = float(d)
                        b += float(m)/60
                        b += float(s)/(60*60)

                        bearing = math.radians(b)

                    (dx,dy,bearing_new) = self.compute_dxdy_from_straightline(bearing,float(di))

                    t.seth((90-math.degrees(bearing_new))%360)
                    t.forward(float(di))

                    x+=dx
                    y+=dy
                    bearing = bearing_new

                    if float(di)<0:
                        # If a distance is negative, treat that as 180 in the other way
                        bearing+=math.radians(180)

                    distance+=abs(float(di))
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
            padding = 1.1

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

        dist = math.sqrt(x**2+y**2)

        closure = float('inf')      
        # To avoid a /0 error, only divide if dist is not equal to 0. (closure is listed as 1/n and a perfect closure means 1/0)
        if dist!=0:
            closure = distance/dist

        while bearing>2*math.pi:
            bearing-=2*math.pi

        b_degrees = bearing*180/math.pi

        b_d = math.floor(b_degrees)
        b_min = (b_degrees-b_d)*60
        b_m = math.floor(b_min)
        b_s = (b_min-b_m)*60

        t.color("black")
        t.write("Closure: 1/%.0f \nd:%.3f di: %.3f\n(x: %.3f, y: %.3f)\nBearing: %d-%d-%.3f"%(closure,dist,distance,x,y,b_d,b_m,b_s))

        self.tscreen.update()  # Turn off automatic screen updates

        self.currently_drawing = False
    
    def compute_dxdy_from_straightline(self,rads,di):
        # Using a distance and angle, compute the next set of coords (direct problem)
        (dx,dy) = self.compute_direct(di,rads)

        return (dx,dy,rads)

    def compute_dxdy_from_curve_delta(self,rad_bearing,rad,r):
        # Using a starting bearing, curve radius and bearing, compute the next set of coords
        # This is done by going towards the radius, adding the angle, and then going going away
        bearing_towards = rad_bearing-math.radians(90)
        bearing_away = bearing_towards-math.radians(180)-rad
        bearing_new = bearing_away-math.radians(90)

        (dx1,dy1) = self.compute_direct(r,bearing_towards)
        (dx2,dy2) = self.compute_direct(r,bearing_away)

        dx = dx1+dx2
        dy = dy1+dy2

        return (dx,dy,bearing_new)

    def compute_direct(self,dist,rad):
        # Computes the direct problem (give change in distance using distance and radius)
        dx = dist*math.cos(rad)
        dy = dist*math.sin(rad)

        return (dx,dy)
    


if __name__ == "__main__":
    app = ClosureCalc()
    app.mainloop()
