import tkinter as tk
from closure_keybind_actions import keybind_actions
from consts import FIELDS_NEEDED

"""
Hoping this will store all the rows. 
"""
class rows_controller():
    def __init__(self,app):
        # Reference back to the main app
        self.app = app
        # The actual row arrays
        self.rows = []
        # The "id" that will be unique, starting at 1 going up
        self.row_id = 1
        # Helper function to house any keyboard actions
        self.key_actions = keybind_actions(app, self.rows)

    def get_row_length(self):
        return len(self.rows)

    def add_row(self, index = get_row_length()):
        # Each row is just a dict of widgets to grid
        row_widgets = {}

        # Since this is a port over we will steal the scrollable frame over from app
        # TODO maybe refactor and include this over here?
        scrollable_frame = self.app.scrollable_frame

        # Construct the widgets
        # Starting with the checkbox (and its bool val)
        curve_var = tk.BooleanVar()
        curve_check = tk.Checkbutton(
            scrollable_frame,
            variable=curve_var,
            command=self.regrid_rows
        )
        row_widgets["curve"] = curve_var
        row_widgets["check"] = curve_check

        rid = self.row_id # So we dont have to keep on getting
        kb = self.key_actions

        for field in FIELDS_NEEDED:
            # Add entry box and add bindings
            row_widgets[field] = tk.Entry(scrollable_frame, width=10)
            row_widgets[field].bind("<FocusOut>", lambda e, r=row_widgets: kb.on_entry_edit(r))
            row_widgets[field].bind("<Shift-Down>", lambda e, f=field, i=rid: kb.focus_next_row_field(i, f))
            row_widgets[field].bind("<Shift-Up>", lambda e, f=field, i=rid: kb.focus_prev_row_field(i, f))
            row_widgets[field].bind("<Down>", lambda e, f=field, i=rid: kb.focus_next_row_field(i, f))
            row_widgets[field].bind("<Up>", lambda e, f=field, i=rid: kb.focus_prev_row_field(i, f))
            row_widgets[field].bind("<Return>", lambda e, f=field, i=rid: kb.focus_next_row_field_return(i, f))
            row_widgets[field].bind("<Shift-Left>", lambda e, f=field, i=rid: kb.focus_prev_field_in_row(i, f))
            row_widgets[field].bind("<Shift-Right>", lambda e, f=field, i=rid: kb.focus_next_field_in_row(i, f))
            row_widgets[field].bind("<space>", lambda e, f=field, i=rid: kb.toggle_curve(i, f))

        def make_insert_callback(index):
            return lambda: self.insert_row_at(index)

        def make_remove_callback(index):
            return lambda: self.remove_row_at(index)

        row_widgets["insert_btn"] = tk.Button(
            scrollable_frame,
            text="+",
            width=2,
            command=make_insert_callback(index)
        )

        row_widgets["remove_btn"] = tk.Button(
            scrollable_frame,
            text="-",
            width=2,
            command=make_remove_callback(index)
        )

        row_widgets["id"] = self.row_id

        self.row_id+=1

        self.rows.insert(index, row_widgets)
        self.app.regrid_rows()