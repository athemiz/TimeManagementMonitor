import tkinter as tk
import numpy as np
import queue
import pystray
import threading
from functools import partial
from pynput import keyboard
from tkinter import ttk
from tooltip import ToolTip
from datetime import datetime
from google_calendar import get_events_for_today
from task_data import load_tasks
from utils import calculate_task_size, calculate_task_position, calculate_time_mark_percentage, get_taskbar_height_and_position
from PIL import Image
from pystray import MenuItem as item
import winsound
import time

class TaskManagerMonitor(tk.Tk):    
    def __init__(self):
        super().__init__()
        self.title('Task Manager Monitor')
        taskbar_height, taskbar_position = get_taskbar_height_and_position()
        self.sync_active, self.sync_id, self.opacity = False, None, 0.5
        self.taskWindowSizeY, self.taskWindowPosY = taskbar_height, taskbar_position[1]
        self.timeBarTickness, self.isTaskViewOpen, self.usedColors, self.taskList = 4, False, [], []
        
        self.played_sounds = set()

        # Create a Notebook widget to handle tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Create the 'Main' and 'Shortcuts' tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.shortcuts_tab = ttk.Frame(self.notebook)

        # Add the tabs to the notebook
        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.shortcuts_tab, text="Shortcuts")

        # Create the widgets for each tab
        self.create_main_widgets()
        self.create_shortcuts_widgets()

        self.tasks = load_tasks()

        self.event_queue = queue.Queue()  # Add a new Queue object
        self.process_queue()  # Process the queue initially

        # Setup the hotkey
        self.alt_pressed = False
        self.hotkey_listener = keyboard.Listener(on_press=self.on_key_press)
        self.hotkey_listener.start()

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.mainloop()

    def play_sound_effect(self):
        winsound.PlaySound("sound_effect.wav", winsound.SND_FILENAME)

    def on_key_press(self, key):
        if key == keyboard.Key.alt_l:
            self.alt_pressed = True
        elif self.alt_pressed and key == keyboard.KeyCode.from_char('t'):
            self.event_queue.put(partial(self.toggle_topmost))

    def on_key_release(self, key):
        if key == keyboard.Key.alt_l:
            self.alt_pressed = False

    def toggle_topmost(self):
        if self.isTaskViewOpen:
            topmost_state = self.taskWindow.attributes('-topmost')
            self.taskWindow.attributes('-topmost', not topmost_state)

    def process_queue(self):
        while not self.event_queue.empty():
            try:
                task = self.event_queue.get_nowait()
                task()
            except queue.Empty:
                pass
        self.after(100, self.process_queue)  # Schedule the next queue processing in 100 ms

    def create_main_widgets(self):
        main_frame = ttk.Frame(self.main_tab, padding="10 10 10 10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        self.sync_var = tk.IntVar()
        self.sound_var = tk.IntVar()

        def grid_widget(widget, column, row, **kwargs):
            widget.grid(column=column, row=row, **kwargs)
            return widget

        task_label = grid_widget(ttk.Label(main_frame, text='Task Name:'), 1, 1, sticky=tk.W)
        self.taskNameInput = grid_widget(ttk.Entry(main_frame, width=30), 2, 1, columnspan=3, sticky=(tk.W, tk.E))
        self.open_task_view_button = grid_widget(ttk.Button(main_frame, text='Open Task View', command=self.toggle_task_view), 5, 2, padx=(10, 0), sticky=tk.W)

        time_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
        grid_widget(ttk.Label(main_frame, text='Begin Time:'), 1, 2, sticky=tk.W)
        self.taskBeginInput = grid_widget(ttk.Combobox(main_frame, values=time_options, width=10), 2, 2, sticky=tk.W)
        end_label = grid_widget(ttk.Label(main_frame, text='End Time:'), 3, 2, sticky=tk.W)
        self.taskEndInput = grid_widget(ttk.Combobox(main_frame, values=time_options, width=10), 4, 2, sticky=tk.W)
        add_task_button = grid_widget(ttk.Button(main_frame, text='Add Task', command=self.add_task), 5, 0, rowspan=2, padx=(10, 0), sticky=tk.W)

        sync_settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10 10 10 10")
        sync_settings_frame.grid(column=1, row=3, columnspan=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.sync_checkbox = grid_widget(tk.Checkbutton(sync_settings_frame, text="Sync with Google Calendar", variable=self.sync_var, command=self.toggle_sync), 1, 1, sticky=tk.W, padx=(10, 0))
        self.interval_combobox = grid_widget(ttk.Combobox(sync_settings_frame, state="readonly", width=10, values=("1 min", "5 min", "10 min", "30 min", "1 hour")), 2, 1, padx=(10, 0), sticky=tk.W)
        self.interval_combobox.current(4)

        sync_calendar_button = grid_widget(ttk.Button(main_frame, text='Sync Calendar', command=self.start_add_events_thread), 5, 4, padx=(10, 0), sticky=tk.W)

        sync_calendar_button.grid(column=5, row=4, padx=(10, 0), sticky=tk.W)

        # Add the sound checkbox
        self.sound_checkbox = grid_widget(tk.Checkbutton(sync_settings_frame, text="Play sound on task start", variable=self.sound_var), 1, 2, sticky=tk.W, padx=(10, 0))

    def start_add_events_thread(self):
        thread = threading.Thread(target=self.add_events_from_calendar, daemon=True)
        thread.start()

    def create_shortcuts_widgets(self):
        # Add widgets related to keyboard shortcuts in the shortcuts_tab
        shortcuts_frame = ttk.Frame(self.shortcuts_tab, padding="10 10 10 10")
        shortcuts_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add content (labels, buttons, etc.) for the keyboard shortcuts tab
        example_shortcut_label = ttk.Label(shortcuts_frame, text="Alt+T: Toggle taskbar topmost attribute on/off")
        example_shortcut_label.grid(column=0, row=0, sticky=tk.W)

    def toggle_task_view(self):
        if not self.isTaskViewOpen:
            self.open_task_window()
            self.open_task_view_button.configure(text='Close Task View')
        else:
            self.close_task_window()
            self.open_task_view_button.configure(text='Open Task View')

    def open_task_window(self):
        self.taskWindow = tk.Tk()
        self.taskWindow.attributes('-alpha', self.opacity, '-topmost', True)
        self.taskWindow.resizable(False, False)
        self.taskWindow.geometry("%dx%d+%d+%d" % (self.taskWindow.winfo_screenwidth(), self.taskWindowSizeY, 0, self.taskWindowPosY))
        self.taskWindow.overrideredirect(True)
        self.isTaskViewOpen = True
        self.refresh_task_bar()

    def close_task_window(self):
        if self.isTaskViewOpen:
            self.taskWindow.destroy()
            self.isTaskViewOpen = False

    def toggle_sync(self):
        if self.sync_var.get() == 1:
            interval = self.get_sync_interval()
            self.start_sync(interval)
        else:
            self.stop_sync()

    def quit(self):
        if self.icon:
            self.icon.stop()
        super().quit()

    def start_sync(self, interval):
        if not self.sync_active:
            self.sync_active = True
            self.sync_loop(interval)

    def stop_sync(self):
        if self.sync_active:
            self.sync_active = False
            if self.sync_id is not None:
                self.after_cancel(self.sync_id)
                self.sync_id = None

    def sync_loop(self, interval):
        if self.sync_active:
            self.start_add_events_thread()
            self.sync_id = self.after(interval * 1000, self.sync_loop, interval)

    def get_sync_interval(self):
        interval = self.interval_combobox.get().split(" ")[0]
        if "min" in self.interval_combobox.get():
            return int(interval) * 60
        else:
            return int(interval) * 60 * 60

    def refresh_task_bar(self):
        self.clear_task_bar()
        current_day = datetime.now().strftime("%A").lower()
        if current_day in self.tasks:
            for task in self.tasks[current_day]:
                task_name, begin_time, end_time, task_color = task.values()
                self.create_task(task_name, begin_time, end_time, task_color)
        for task in self.taskList:
            self.create_task(task[0], task[1], task[2], task[3])
        self.draw_time_rectangle()

        # Play sound effect when it's time to start a new task
        current_time = datetime.now().strftime("%H:%M")
        for task in self.taskList:
            if task[1] == current_time and task[1] not in self.played_sounds:
                for _ in range(3):
                    if self.sound_var.get() == 1:
                        self.play_sound_effect()
                        time.sleep(1)
                self.played_sounds.add(task[1])
                break

        self.taskWindow.after(1000, self.refresh_task_bar)

    def clear_task_bar(self):
        if self.isTaskViewOpen:
            for widget in self.taskWindow.winfo_children():
                widget.destroy()

    def generate_random_color(self):
        while True:
            color = list(np.random.choice(range(256), size=3))
            if color not in self.usedColors:
                self.usedColors.append(color)
                break
        return "#%02x%02x%02x" % (color[0], color[1], color[2])

    def add_task(self):
        taskName = self.taskNameInput.get()
        beginTime = self.taskBeginInput.get()
        endTime = self.taskEndInput.get()
        taskColor = self.generate_random_color()
        self.taskList.append([taskName, beginTime, endTime, taskColor])
        self.tasks[taskName] = (beginTime, endTime, taskColor)

    def create_task(self, taskName, beginTime, endTime, taskColor):
        taskRectangleSize = calculate_task_size(beginTime, endTime, self.taskWindow.winfo_screenwidth())
        taskRectangle = tk.Frame(self.taskWindow, width=taskRectangleSize, height=self.taskWindowSizeY, bg=taskColor)
        taskRectangle.place(relx=calculate_task_position(beginTime), rely=0.5, anchor=tk.W)
        tipMessage = taskName + " " + beginTime + " - " + endTime
        tip = ToolTip(self.taskWindow, tipMessage)
        taskRectangle.bind('<Enter>', lambda event: self.show_tooltip(event, tip))
        taskRectangle.bind('<Leave>', lambda event: self.hide_tooltip(event, tip))

    def add_events_from_calendar(self):
        events = get_events_for_today()
        if events:
            for task_name, start_time, end_time in events:
                start_time = datetime.fromisoformat(start_time).strftime('%H:%M')
                end_time = datetime.fromisoformat(end_time).strftime('%H:%M')
                task_color = self.generate_random_color()
                self.taskList.append([task_name, start_time, end_time, task_color])
        else:
            print('No events found for today.')

    def add_task_from_calendar(self, task_name, start_time, end_time):
        self.taskNameInput.delete(0, tk.END)
        self.taskNameInput.insert(0, task_name)
        self.taskBeginInput.delete(0, tk.END)
        self.taskBeginInput.insert(0, start_time)
        self.taskEndInput.delete(0, tk.END)
        self.taskEndInput.insert(0, end_time)
        self.add_task()

    def show_tooltip(self, event, tooltip):
        x, y, _, _ = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 20
        y += event.widget.winfo_rooty() + 20
        tooltip.show(x, y)

    def hide_tooltip(self, event, tooltip):
        tooltip.hide()

    def draw_time_rectangle(self):
        timeMarkRectangle = tk.Canvas(self.taskWindow, width=self.timeBarTickness, height=self.taskWindowSizeY, bg='black')
        timeMarkRectangle.place(relx=calculate_time_mark_percentage(), rely=0.5, anchor=tk.W)

    def open_task_view(self):
        if not self.isTaskViewOpen:
            self.taskWindow = tk.Tk()
            self.taskWindow.attributes('-alpha', self.opacity, '-topmost', True)
            self.taskWindow.resizable(False, False)
            self.taskWindow.geometry("%dx%d+%d+%d" % (self.taskWindow.winfo_screenwidth(), self.taskWindowSizeY, 0, self.taskWindowPosY))
            self.taskWindow.overrideredirect(True)
            self.isTaskViewOpen = True
            self.refresh_task_bar()

    def tray_icon_clicked(self, icon, action):
        icon.stop()
        self.deiconify()

    def create_bindings(self):
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def minimize_to_tray(self):
        self.withdraw()
        image = Image.open("icon.png")  # Replace "icon.png" with the path to your icon file
        menu = (item('Open', self.tray_icon_clicked), item('Exit', self.quit))
        self.icon = pystray.Icon("Task Manager Monitor", image, "Task Manager Monitor", menu)
        icon_thread = threading.Thread(target=self.icon.run)
        icon_thread.start()
        

if __name__ == "__main__": TaskManagerMonitor()