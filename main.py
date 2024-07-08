#!/usr/bin/env python3
"""
    To install the Tkinter on popular Linux distros:
    ------------------------------------------------
    Debian/Ubuntu:
    sudo apt install python3-tk -y

    Fedora:
    sudo dnf install -y python3-tkinter

    Arch:
    sudo pacman -Syu tk --noconfirm

    REHL/CentOS6/CentOS7:
    sudo yum install -y python3-tkinter

    OpenSUSE:
    sudo zypper in -y python-tk
"""
import tkinter as tk
from tkinter import filedialog, messagebox


class ADIFileApp:
    def __init__(self, root):
        self.anzahl = None
        self.root = root
        self.root.title("ADI/ADIF File Editor")

        self.file_path = tk.StringVar()
        self.records = []
        self.filtered_records = []
        self.current_record_index = -1
        self.filters = {}
        self.is_filtered = False
        self.last_saved_index = -1

        self.create_widgets()
        self.create_bindings()

    def create_widgets(self):
        tk.Label(self.root, text="ADI/ADIF File Path:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.file_path, width=50).grid(row=0, column=1, columnspan=2, sticky=tk.W)
        tk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=3, sticky=tk.E)

        tk.Button(self.root, text="Load", command=self.load_file).grid(row=0, column=4, sticky=tk.E)

        self.fields_frame = tk.Frame(self.root)
        self.fields_frame.grid(row=1, column=0, columnspan=6, sticky=tk.W)

        # Placeholder for buttons to appear after loading data
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=2, column=0, columnspan=6, sticky=tk.W)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=6, sticky=tk.W)

    def create_buttons(self):
        tk.Button(self.button_frame, text="Previous", command=self.previous_record).grid(row=0, column=0, sticky=tk.E)
        tk.Button(self.button_frame, text="Next", command=self.next_record).grid(row=0, column=1, sticky=tk.E)
        tk.Button(self.button_frame, text="First", command=self.first_record).grid(row=0, column=2, sticky=tk.E)
        tk.Button(self.button_frame, text="Last", command=self.last_record).grid(row=0, column=3, sticky=tk.E)
        tk.Button(self.button_frame, text="New Record", command=self.new_record).grid(row=1, column=0, sticky=tk.E)
        tk.Button(self.button_frame, text="Save", command=self.confirm_save).grid(row=1, column=1, sticky=tk.E)
        tk.Button(self.button_frame, text="Delete", command=self.confirm_delete).grid(row=1, column=2, sticky=tk.E)
        self.filter_button = tk.Button(self.button_frame, text="Filter", command=self.open_filter_window)
        self.filter_button.grid(row=1, column=3, sticky=tk.E)

    def create_bindings(self):
        self.root.bind("<Left>", lambda e: self.previous_record())
        self.root.bind("<Right>", lambda e: self.next_record())
        self.root.bind("<Home>", lambda e: self.first_record())
        self.root.bind("<End>", lambda e: self.last_record())
        self.root.bind("<Control-s>", lambda e: self.confirm_save())
        self.root.bind("<Control-n>", lambda e: self.new_record())

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path.set(file_path)

    def load_file(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file.")
            return

        try:
            with open(file_path, 'r') as file:
                data = file.read()

            raw_records = data.split('<eor>')
            self.records = [self.parse_record(record) for record in raw_records if record.strip()]
            self.filtered_records = self.records
            self.current_record_index = 0 if self.last_saved_index == -1 else self.last_saved_index
            self.create_buttons()
            self.display_record()
            self.update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def parse_record(self, record):
        fields = {}
        parts = record.split('<')[1:]
        for part in parts:
            if '>' in part:
                tag, value = part.split('>', 1)
                fields[tag] = value.strip()
        return fields

    def display_record(self):
        if self.current_record_index < 0 or self.current_record_index >= len(self.filtered_records):
            return

        record = self.filtered_records[self.current_record_index]

        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        for i, (tag, value) in enumerate(record.items()):
            tk.Label(self.fields_frame, text=f"{tag}:").grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(self.fields_frame, width=50)
            entry.grid(row=i, column=1, sticky=tk.W)
            entry.insert(0, value)
            self.entries[tag] = entry

    def update_status(self):
        total_records = len(self.filtered_records)
        current_record_num = self.current_record_index + 1 if self.filtered_records else 0
        status_text = f"Loaded records: {total_records}, Current record: {current_record_num}"
        self.status_var.set(status_text)

    def previous_record(self):
        if self.current_record_index > 0:
            self.current_record_index -= 1
            self.display_record()
            self.update_status()

    def next_record(self):
        if self.current_record_index < len(self.filtered_records) - 1:
            self.current_record_index += 1
            self.display_record()
            self.update_status()

    def first_record(self):
        if self.filtered_records:
            self.current_record_index = 0
            self.display_record()
            self.update_status()

    def last_record(self):
        if self.filtered_records:
            self.current_record_index = len(self.filtered_records) - 1
            self.display_record()
            self.update_status()

    def delete_record(self):
        if self.current_record_index >= 0 and self.current_record_index < len(self.filtered_records):
            del self.records[self.records.index(self.filtered_records[self.current_record_index])]
            self.filtered_records = self.records
            if self.current_record_index >= len(self.filtered_records):
                self.current_record_index = len(self.filtered_records) - 1
            self.display_record()
            self.update_status()

    def new_record(self):
        default_record = {
            'call:0': '', 'gridsquare:0': '', 'mode:0': '', 'rst_sent:0': '', 'rst_rcvd:0': '',
            'qso_date:0': '', 'time_on:0': '', 'qso_date_off:0': '', 'time_off:0': '',
            'band:0': '', 'freq:0': '', 'station_callsign:0': '', 'my_gridsquare:0': '',
            'tx_pwr:0': '', 'comment:0': '', 'eqsl_qsl_sent:0': ''
        }
        self.records.append(default_record)
        self.filtered_records = self.records
        self.current_record_index = len(self.filtered_records) - 1
        self.display_record()
        self.update_status()

    def confirm_save(self):
        if messagebox.askyesno("Confirm Save", "Are you sure you want to save the changes?"):
            self.save_file()
            self.load_file()  # Refresh the records after saving        # Logic to save the current record

    def save_file(self):
        self.save_current_record()
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file.")
            return

        try:
            self.last_saved_index = self.current_record_index  # Speichere den Index des aktuellen Datensatzes
            with open(file_path, 'w') as file:
                for record in self.records:
                    updated_record = self.update_record_lengths(record)
                    record_str = ''.join([f"<{tag}>{value}" for tag, value in updated_record.items()]) + '<eor>\n'
                    file.write(record_str)
            messagebox.showinfo("Success", "Data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def update_record_lengths(self, record):
        updated_record = {}
        for tag, value in record.items():
            if ':' in tag:
                tag_name, _ = tag.split(':')
                updated_tag = f"{tag_name}:{len(value)}"
            else:
                updated_tag = tag
            updated_record[updated_tag] = value
        return updated_record

    def save_current_record(self):
        if self.current_record_index < 0 or self.current_record_index >= len(self.filtered_records):
            return

        record = self.filtered_records[self.current_record_index]
        for tag, entry in self.entries.items():
            record[tag] = entry.get()

    def confirm_delete(self):
        if self.current_record_index >= 0 and self.current_record_index < len(self.filtered_records):
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
            if confirm:
                self.delete_record()

    def open_filter_window(self):
        filter_window = tk.Toplevel(self.root)
        filter_window.title("Filter Records")

        filters = {}

        for i, (tag, _) in enumerate(self.records[self.current_record_index].items()):
            tk.Label(filter_window, text=f"{tag}:").grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(filter_window, width=50)
            entry.grid(row=i, column=1, sticky=tk.W)
            filters[tag] = entry

        def apply_filter():
            self.filters = {tag: entry.get() for tag, entry in filters.items() if entry.get()}
            self.filtered_records = [
                record for record in self.records
                if all(record.get(tag, '').startswith(value) for tag, value in self.filters.items())
            ]
            self.current_record_index = 0
            self.display_record()
            self.update_status()
            self.is_filtered = True
            self.filter_button.config(text="Remove Filter", command=self.remove_filter)
            filter_window.destroy()

        def cancel_filter():
            filter_window.destroy()

        tk.Button(filter_window, text="OK", command=apply_filter).grid(row=len(self.records[0]) +1, column=0, sticky=tk.W)
        tk.Button(filter_window, text="Cancel", command=cancel_filter).grid(row=len(self.records[0]) +1, column=1, sticky=tk.W)

    def remove_filter(self):
        self.filters = {}
        self.filtered_records = self.records
        self.current_record_index = 0
        self.display_record()
        self.update_status()
        self.is_filtered = False
        self.filter_button.config(text="Filter", command=self.open_filter_window)


if __name__ == "__main__":
    root = tk.Tk()
    app = ADIFileApp(root)
    root.mainloop()
