import numpy as np
from enum import Enum
import sys

import mso54 as analyzer


class State(Enum):
    BUSY = 'busy'
    DISCONNECTED = 'disconnected'
    CONNECTED = 'connected'


class Model:

    # constructor & destructor
    def __init__(self):
        self.instrument = analyzer.MSO54()
        self._observers = set()
        self.state = State.DISCONNECTED
        self.available_channels = None

    def __del__(self):
        pass

    # model specific methods
    def timer_routine(self):
        # print('timer routine called')
        if self.state is not State.CONNECTED:
            try:
                self.instrument.connect()
            except analyzer.NoConnectionError:
                print('NoConnectionError')
                pass
            except analyzer.WrongInstrumentError:
                print('WrongInstrumentError')
                pass
        if self.instrument.is_connected():
            self.state = State.CONNECTED
            self.available_channels = self.instrument.get_available_channels()
        else:
            self.state = State.DISCONNECTED
        # self.instrument.acquire_single_sequence(wait_for_completion=True)


    def data(self, channel):
        if self.state == State.CONNECTED:
            try:
                time, data, sample_period = self.instrument.transfer_waveform(channel)
                return {"time": time,
                        "data": data,
                        "sample_period": sample_period}
            except analyzer.VisaError as error:
                print('VISA error: {0}'.format(error))
        else:
            return None

    # observer pattern methods
    def attach(self, observer):
        self._observers.add(observer)

    def detach(self, observer):
        self._observers.discard(observer)

    def __notify(self):
        for observer in self._observers:
            observer.update(self.__state)

    def get_available_channels(self):
        return self.available_channels

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, arg):
        self.__state = arg
        self.__notify()
