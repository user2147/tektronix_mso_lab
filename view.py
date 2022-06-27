import tkinter as tk
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from tkinter import ttk


from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import warnings

import numpy as np


class View:
    # constructor
    def __init__(self, control):
        self.control = control
        self.window = tk.Tk()
        self.window.title(self.control.window_title)
        self.window.geometry('640x480')

        # create all of the main containers
        toolbar_frame = tk.Frame(self.window, bg='white', width=640, height=50)
        canvas_frame = tk.Frame(self.window, bg='white', width=640, height=330)
        rbutton_frame = tk.Frame(self.window, bg='white', width=640, height=50, pady=10)
        button_frame = tk.Frame(self.window, bg='white', width=640, height=100, pady=10)
        statusbar_frame = tk.Frame(self.window, bg='white', width=640, height=50)
        # layout all of the main containers
        toolbar_frame.pack(fill=tk.X)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        rbutton_frame.pack(fill=tk.X)
        button_frame.pack(fill=tk.X)
        statusbar_frame.pack(fill=tk.X)

        # create the widgets for the canvas frame
        self.fig = Figure(figsize=(1, 1), dpi=100)
        t = np.arange(0, 3, .01)
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = self.ax1.twinx()  # instantiate a second axes that shares the same x-axis
        # self.ax.plot(np.arange(0, 3, .01), 2 * np.sin(2 * np.pi * t))
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)  # A tk.DrawingArea.
        self.canvas.draw()
        # layout the widgets in the canvas frame
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # create the widgets for the toolbar frame
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.config(background='white')
        for button in toolbar.winfo_children():
            button.config(background='white')
        toolbar.update()
        # layout the widgets in the toolbar frame
        toolbar.pack(side=tk.TOP)

        # create the widgets for the radio button frame
        font_1 = font.Font(family='Helvetica', size=14, weight='bold')
        ttk.Label(rbutton_frame, text='Choose channel:', font=font_1, background='white').pack(side=tk.LEFT, padx=15)
        self.channel = tk.StringVar()
        self.channel_box = ttk.Combobox(rbutton_frame, width=27, textvariable=self.channel, state='readonly')
        self.channel_box.pack(side=tk.LEFT, padx=15)

        # create the widgets for the button frame
        helv36 = font.Font(family='Helvetica', size=18, weight='bold')
        tk.Button(button_frame, text="read", command=self.control.button_read_click,
                  padx=20, pady=10, font=helv36).pack(side=tk.LEFT, expand=True)
        tk.Button(button_frame, text="import", command=self.control.button_import_click,
                  padx=20, pady=10, font=helv36).pack(side=tk.LEFT, expand=True)
        tk.Button(button_frame, text="export", command=self.control.button_export_click,
                  padx=20, pady=10, font=helv36).pack(side=tk.LEFT, expand=True)

        # create the widgets for the statusbar frame
        self.statusbar = tk.Label(statusbar_frame, text="MSO54: undefined state", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        # layout the widgets in the statusbar frame
        self.statusbar.pack(fill=tk.X)

    # destructor
    def __del__(self):
        pass

    # public methods
    # show() has to be called at very last as the mainloop() blocks every line of code coming after
    def show(self):
        self.window.mainloop()

    def update_statusbar(self, status):
        self.statusbar['text'] = 'MSO54: ' + status

    def update_available_channels(self, available_channels):
        self.channel_box['values'] = available_channels

    def timer(self, interval_ms, func):
        self.window.after(interval_ms, lambda: self.__timer_routine(interval_ms, func))

    def __timer_routine(self, interval_ms, func):
        func()
        self.window.after(interval_ms, lambda: self.__timer_routine(interval_ms, func))

    def simple_plot(self, x, y):
        self.ax1.plot(x, y, linestyle='-')
        self.ax1.grid(b=True, which='both', axis='both')
        # self.ax1.legend(loc='upper right')
        self.ax1.margins(x=0)
        self.ax1.set_xlabel('time in s')
        self.ax1.set_ylabel('voltage in V')
        self.fig.tight_layout()
        self.canvas.draw()

    # def loglog_plot(self, x, y1, y2):
    #     self.ax1.set_xlabel('freq / Hz')
    #     self.ax1.set_ylabel('Trace A')
    #     self.ax1.loglog(x, y1, linestyle='-')
    #     self.ax2.set_ylabel('Trace B')
    #     self.ax2.semilogx(x, y2, linestyle=':')
    #     self.canvas.draw()

    # def semilogx_plot(self, x, y1, y2, label=None):
    #     # self.ax1.semilogx(x, y1, linestyle='-', color='red', label=label1)
    #     # self.ax2.semilogx(x, y2, linestyle=':', color='blue', label=label2)
    #     # self.ax1.set_xlabel('freq / Hz')
    #     # self.ax1.set_ylabel('Trace A')
    #     # self.ax2.set_ylabel('Trace B')
    #     # self.ax1.yaxis.label.set_color('red')
    #     # self.ax2.yaxis.label.set_color('blue')
    #     # self.ax1.tick_params(axis='y', colors='red')
    #     # self.ax2.tick_params(axis='y', colors='blue')
    #     # self.ax2.spines['left'].set_color('red')
    #     # self.ax2.spines['right'].set_color('blue')
    #     self.ax1.set_xlabel('freq / Hz')
    #     self.ax1.set_ylabel('Trace A (solid -)')
    #     self.ax1.semilogx(x, y1, linestyle='-', label=label)
    #     self.ax2.set_ylabel('Trace B (dotted :)')
    #     self.ax2.semilogx(x, y2, linestyle=':')
    #     if label is not None:
    #         self.ax1.legend()
    #     self.canvas.draw()

    def show_errorbox(self, title, message):
        messagebox.showerror(title, message)

    def show_warningbox(self, title, message):
        messagebox.showwarning(title, message)

    def save_as_csvfile_dialog(self):
        return filedialog.asksaveasfile(mode='wb', defaultextension=".npz",
                                        filetypes=(("compressed numpy arrays", "*.npz"), ("all files", "*.*")))

    def read_as_csvfile_dialog(self):
        return filedialog.askopenfile(mode='rb', defaultextension=".npz",
                                      filetypes=(("compressed numpy arrays", "*.npz"), ("all files", "*.*")))
