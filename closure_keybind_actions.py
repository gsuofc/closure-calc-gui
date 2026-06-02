import tkinter as tk
from consts import FIELDS_NEEDED

class keybind_actions:
    def __init__(self, app, rows):
        self.app = app
        self.rows = rows

    def toggle_curve(self, index, field):
        cur_row = 0
        for i in self.app.rows:
            if i["id"]==index:
                break
            cur_row +=1

        next_row = self.rows[cur_row]
        next_row["curve"].set(not next_row["curve"].get())
        self.app.regrid_rows()
        text = next_row[field].get().strip()
        next_row[field].delete(0,tk.END)
        next_row[field].insert(0,text)
        return "break"
    
    def focus_next_field_in_row(self, row_id, field):
        current_index = next((i for i, row in enumerate(self.rows) if row["id"] == row_id), None)
        if current_index is None:
            return

        try:
            idx = FIELDS_NEEDED.index(field)
        except ValueError:
            return

        for next_idx in range(idx + 1, len(FIELDS_NEEDED)):
            next_field = FIELDS_NEEDED[next_idx]
            if next_field in self.rows[current_index] and self.rows[current_index][next_field].winfo_viewable():
                self.rows[current_index][next_field].focus_set()
                break

    def focus_prev_field_in_row(self, row_id, field):
        current_index = next((i for i, row in enumerate(self.rows) if row["id"] == row_id), None)
        if current_index is None:
            return

        try:
            idx = FIELDS_NEEDED.index(field)
        except ValueError:
            return

        for prev_idx in range(idx - 1, -1, -1):
            prev_field = FIELDS_NEEDED[prev_idx]
            if prev_field in self.rows[current_index] and self.rows[current_index][prev_field].winfo_viewable():
                self.rows[current_index][prev_field].focus_set()
                break

    def focus_next_row_field(self, index, field):
        cur_row = 0
        for i in self.rows:
            if i["id"]==index:
                break
            cur_row +=1
        next_index = cur_row + 1
        if next_index < len(self.rows):
            next_row = self.rows[next_index]
            if field in next_row and next_row[field].winfo_viewable():
                next_widget = next_row[field]
                next_widget.focus_set()
            else:
                next_widget = next_row["sec"]
                next_widget.focus_set()

    def focus_next_row_field_return(self, index, field):
        cur_row = 0
        for i in self.rows:
            if i["id"]==index:
                break
            cur_row +=1
        next_index = cur_row + 1
        if next_index < len(self.rows):
            next_row = self.rows[next_index]
            next_widget = next_row["deg"]
            next_widget.focus_set()

    def focus_prev_row_field(self, index, field):
        cur_row = 0
        for i in self.rows:
            if i["id"]==index:
                break
            cur_row +=1
        prev_index = cur_row - 1
        if prev_index >= 0:
            prev_row = self.rows[prev_index]
            if field in prev_row and prev_row[field].winfo_viewable():
                next_widget = prev_row[field]
                next_widget.focus_set()
            else:
                next_widget = prev_row["sec"]
                next_widget.focus_set()

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
        self.app.compute_closure()