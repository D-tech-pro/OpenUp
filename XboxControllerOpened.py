import tkinter as tk
from tkinter import filedialog, messagebox
import hid
import time
import threading
import subprocess
import os
import json

CONFIG_FILE = 'xbox_launcher_config.json'

class XboxControllerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title('Xbox Controller EXE Launcher')

        self.exe_path = tk.StringVar()
        self.controller_connected = False
        self.monitoring = True
        self.process = None

        # Load saved configuration if exists
        self.load_config()

        # GUI Elements
        self.create_widgets()

        # Start the controller monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_controller)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def create_widgets(self):
        # EXE Path Entry
        self.entry = tk.Entry(self.root, textvariable=self.exe_path, width=50)
        self.entry.grid(row=0, column=0, padx=10, pady=10)

        # Browse Button
        self.browse_button = tk.Button(self.root, text='Browse', command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)

        # Save Button
        self.save_button = tk.Button(self.root, text='Save', command=self.save_config)
        self.save_button.grid(row=1, column=0, columnspan=2, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Executable Files', '*.exe')])
        if file_path:
            self.exe_path.set(file_path)

    def save_config(self):
        config = {'exe_path': self.exe_path.get()}
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file)
        messagebox.showinfo('Saved', 'Configuration saved successfully.')

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
                self.exe_path.set(config.get('exe_path', ''))

    def find_xbox_controller(self):
        for device in hid.enumerate():
            if device['vendor_id'] == 0x045E and 'controller' in device['product_string'].lower():
                return device['path']
        return None

    def monitor_controller(self):
        while self.monitoring:
            controller_path = self.find_xbox_controller()

            if controller_path and not self.controller_connected:
                self.controller_connected = True
                self.on_controller_connected()
            elif not controller_path and self.controller_connected:
                self.controller_connected = False
                self.on_controller_disconnected()

            time.sleep(1)

    def on_controller_connected(self):
        print('Xbox Controller Connected')

        if self.exe_path.get():
            try:
                self.process = subprocess.Popen([self.exe_path.get()])
            except Exception as e:
                messagebox.showerror('Error', f'Failed to launch EXE: {str(e)}')

    def on_controller_disconnected(self):
        print('Xbox Controller Disconnected')

        if self.process:
            try:
                self.process.terminate()
                self.process.wait()
                self.process = None
            except Exception as e:
                messagebox.showerror('Error', f'Failed to close EXE: {str(e)}')

    def on_closing(self):
        self.monitoring = False
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = XboxControllerLauncher(root)
    root.protocol('WM_DELETE_WINDOW', app.on_closing)
    root.mainloop()
