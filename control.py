import numpy as np

from view import View  # '.' indicates relative import
import threading
import os


class Control:
    WINDOW_TITLE = 'Tektronix MSO54 Lab'

    # constructor
    def __init__(self, model):
        # create view object (MVC-pattern)
        self.view = View(self)
        self.model = model
        self.model.attach(self)  # control is now an observer of model (update(model_state))
        self.view.timer(1000, self.model.timer_routine)
        # threading.Timer(10, lambda: self.__timer_routine(1, self.model.timer_routine)).run()
        self.data = {"sample_period": None, "data": None, "time": None}
        self.label = None

    # public methods
    # def __timer_routine(self, interval_ms, func):
    #     func()
    #     threading.Timer(interval_ms, lambda: self.__timer_routine(interval_ms, func)).run()
    #     pass

    @property
    def window_title(self):
        return self.WINDOW_TITLE

    def update(self, model_state):
        self.view.update_statusbar(model_state.value)
        self.view.update_available_channels(self.model.get_available_channels())

    def run(self):
        # view.show() has to be called at very last as the tkinter mainloop() blocks every line of code coming after
        self.view.show()

    def button_import_click(self):
        self.__file_import()
        if self.data is None:
            self.view.show_errorbox('No data retrieved from file.',
                                    'Please check file.')
        else:
            self.view.simple_plot(self.data["time"], self.data["data"])

    def button_export_click(self):
        # in a future version the user is asked in which format he wants to export
        # options will be:
        #   - as new .csv
        #   - as new .lib file (Saves data as a SPICE subcircuit)
        #   - append to existing .lib file (file will be checked for duplicate and user asked for name change/overwrite)
        self.__file_save()

    def button_read_click(self):
        # read in data and show immediately in diagram
        self.data = self.model.data(self.view.channel.get())
        if self.data is None:
            self.view.show_errorbox('No data retrieved from instrument',
                                    'Please check connection, VISA driver, instrument status...')
        else:
            if len(self.data["time"]) > 1e6:
                self.view.show_warningbox('Plotting', 'Too much data to be plotted here.')
            else:
                self.view.simple_plot(self.data["time"], self.data["data"])

    # private methods
    def __file_save(self):
        f = self.view.save_as_csvfile_dialog()
        if f is None:
            return
        print('Start saving data to file...', end='')
        # np.save(f, self.data["time"])
        # np.savez(f, time=self.data["time"], data=self.data["data"])
        np.savez(f, sample_period=self.data["sample_period"], data=self.data["data"])
        # np.savez_compressed(f, time=self.data["time"], data=self.data["data"])
        f.close()
        print(' finished.')

    def __file_import(self):
        f = self.view.read_as_csvfile_dialog()
        if f is None:
            return
        print('Start importing data from file...', end='')
        raw_data = np.load(f)
        # the dictionary fields in raw_data have to be actively called in order to decompress and store the array in
        # memory before being able to close the file with f.close()
        # self.data["time"] = raw_data["time"]
        self.data["sample_period"] = raw_data["sample_period"]
        self.data["data"] = raw_data["data"]
        self.data["time"] = np.linspace(0, (len(raw_data["data"])-1) * raw_data["sample_period"], len(raw_data["data"]))
        self.label = os.path.basename(f.name)
        f.close()
        print(' finished.')
