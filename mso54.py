#!/usr/bin/env python
""" Module for interfacing with the Tektronix MSO54.

Currently only a small subset of commands is implemented. Feel free to add some more from the
"5 Series MSO MSO54, MSO56, MSO58, MSO58LP ZZZ Programmer Manual"
"""

import numpy as np
from enum import Enum
from enum import unique
import pyvisa as visa
from time import sleep


class NoConnectionError(Exception):
    """Could not connect to the VISA instrument

    This error can have multiple reasons. Either the VISA driver, the VISA address or the instrument itself.
    """
    pass


class WrongInstrumentError(Exception):
    """The wrong instrument is connected

    A connection was successfuly established, and the instrument responded
    to a request to identify itself, but the ID received was wrong.
    Probably the instrument at the given VISA identifier is not the one
    you wanted.
    """
    pass


class DataTransferError(Exception):
    """data transfer from the instrument has been corrupted
    """
    pass


class VisaError(Exception):
    pass


@unique
class WaveType(Enum):
    ANALOG = 1
    DIGITAL = 2
    MATH = 3


class MSO54:
    # constants
    # NAME = 'MSO54'
    NAME = 'MSO'

    # TRACE_A_CMD = 'XMA? 0,'
    # TRACE_B_CMD = 'XMB? 0,'
    # FREQUENCY_CMD = 'FQM? 0,'
    # NUMBER_OF_POINTS_CMD = 'MEP?'

    # constructor & destructor
    def __init__(self, visa_address=None):
        self.__visa_manager = visa.ResourceManager()
        self.__visa_address = visa_address
        self._inst = None

    def __del__(self):
        pass

    # VISA methods
    # connect to instrument (either by direct addressing or an automatic search)
    def connect(self):
        if self.__visa_address is None:
            self._search_instrument()
        else:
            try:
                self._inst = self.__visa_manager.open_resource(self.__visa_address)
                self._inst.write('*cls')  # clear Standard Event Status Register red with "*ESR?"
            except visa.errors.VisaIOError:
                raise NoConnectionError('Cannot connect to instrument. Check VISA driver and/or connections.')
            else:
                if self.NAME.lower() not in self._inst.query("*IDN?").lower():
                    self.disconnect()
                    raise WrongInstrumentError('Wrong VISA address. This is not the ' + self.NAME + '.')

    # automatic search for the MSO54 within the connected VISA instruments
    def _search_instrument(self):
        instruments = self.__visa_manager.list_resources()
        candidate = None
        for instrument in instruments:
            try:
                candidate = self.__visa_manager.open_resource(instrument)
            except visa.errors.VisaIOError:
                continue
            if candidate.interface_type == visa.constants.InterfaceType.usb:
                try:
                    if self.NAME.lower() not in candidate.query("*IDN?").lower():
                        candidate = None  # no, that's not our instrument
                    else:
                        break  # great, we found our instrument
                except visa.VisaIOError:
                    candidate = None
            else:
                candidate.close()
                candidate = None
        if candidate is None:
            raise NoConnectionError('Cannot connect to instrument. Check VISA driver and/or connections.')
        else:
            self._inst = candidate

    def disconnect(self):
        try:
            self._inst.close()
        except AttributeError:  # raised when no instrument connected beforehand (what's just fine)
            pass
        except visa.errors.VisaIOError:  # raised when no instrument connected beforehand (what's just fine)
            pass

    def is_connected(self):
        if self._inst is None:
            return False
        else:
            try:
                self._inst.query("*IDN?")
                return True
            except visa.errors.VisaIOError:
                return False
        pass

    # instrument specific commands
    def clear_SESR_EventQueue_StatusByteReg(self):
        self._inst.write('*CLS')

    # this is the same as pushing the "Single/Seq" button on the instrument
    def acquire_single_sequence(self, wait_for_completion=False):
        if (self._inst.query('ACQuire:STOPAfter?').lower().strip() != "sequence"):
            self._inst.write('ACQuire:STOPAfter SEQuence')  # sets instrument to single sequence mode
        if wait_for_completion:
            self._inst.write('DESE 1')
            self._inst.write('*ESE 1')
            self._inst.write('*SRE 0')
            self._inst.write('ACQUIRE:STATE ON')  # activates a new single shot acquisition
            self._inst.write('*OPC')
            i = 0
            while int(self._inst.query('*ESR?')) != 1:
                sleep(0.1)
                i = i + 1
                assert i < 100, "timeout while waiting for acquisition completion"
        else:
            self._inst.write('ACQUIRE:STATE ON')  # activates a new single shot acquisition

    def get_record_length(self):
        return int(self._inst.query('HORizontal:RECORDLength?').split(' ')[-1])

    def get_available_channels(self):
        channels = self._inst.query('DATa:SOUrce:AVAILable?').strip().split(' ')[-1].split(',')
        # if 'none' not in map(str.lower, channels):
        #     channels = list(map(int, channels))
        return channels

    def set_transfer_source(self, channel):
        channel_str = channel
        if channel_str in self._inst.query('DATa:SOUrce:AVAILable?').strip().split(' ')[-1].split(','):
            return self._inst.write('DATa:SOUrce ' + channel_str)
        else:
            raise ValueError('Invalid channel selected')

    def set_transfer_encoding(self, encoding='ASCII'):
        return self._inst.write('DATa:ENCdg ' + encoding)

    def set_transfer_n_byte(self, num_of_bytes=1):
        return self._inst.write('WFMOutpre:BYT_Nr ' + str(num_of_bytes))

    def set_transfer_start_sample(self, start_sample=1):
        return self._inst.write('DATa:STARt ' + str(start_sample))

    def set_transfer_end_sample(self, stop_sample=62500000):
        return self._inst.write('DATa:STOP ' + str(stop_sample))

    # Fetches the waveform from the instrument and converts it into volts
    def transfer_waveform(self, channel):
        self.setup_waveform_transfer(channel,
                                     encoding='SRIbinary',  # SRIbinary -> little endian
                                     # encoding='SFPbinary',  # SRIbinary -> little endian
                                     n_byte=2,  # SRIbinary is either 1 or 2
                                     # n_byte=4,  # number of bytes (float has 4)
                                     )
        self.clear_SESR_EventQueue_StatusByteReg()  # clear SESR
        print('Start transferring data from instrument...', end='')
        raw_data = self._inst.query_binary_values('CURVe?',  # transfer data command
                                                  # datatype='f',  # float (4 bytes)
                                                  datatype='h',  # signed short (2 bytes signed integer)
                                                  is_big_endian=False,  # SRIbinary -> little endian
                                                  container=np.array,  # return as numpy array
                                                  data_points=self.get_record_length(),
                                                  )
        print(' finished.')

        y_mult = float(self._inst.query('WFMOutpre:YMUlt?').split(' ')[-1])
        y_zero = float(self._inst.query('WFMOutpre:YZEro?').split(' ')[-1])
        # y_off = float(self._inst.query('WFMOutpre:YZEro?').split(' ')[-1])
        x_incr = float(self._inst.query('WFMOutpre:XINcr?').split(' ')[-1])
        x_zero = float(self._inst.query('WFMOutpre:XZEro?').split(' ')[-1])
        pre_trig_record = int(self._inst.query('WFMOutpre:PT_Off?').split(' ')[-1])

        # scaled_data = ((raw_data - y_off) * y_mult) + y_zero
        scaled_data = (raw_data * y_mult) + y_zero  # MSO54: y_off is always zero!
        total_time = (len(raw_data)-1) * x_incr
        t_start = (-1 * pre_trig_record * x_incr) + x_zero
        t_stop = t_start + total_time
        scaled_time = np.linspace(t_start, t_stop, len(raw_data))

        if (int(self._inst.query('*ESR?')) & int('0b00111100', 2)):  # check if any error occurred
            raise DataTransferError('Data transfer has been corrupted.')

        return scaled_time, scaled_data, x_incr

    # Setup the waveform transfer as described in the programmer manual at page 2-90
    def setup_waveform_transfer(self, channel, encoding, n_byte, start_sample=1, end_sample=None):
        self.set_transfer_source(channel)
        self.set_transfer_encoding(encoding)
        self.set_transfer_n_byte(n_byte)
        self.set_transfer_start_sample(start_sample)
        if end_sample is None:
            end_sample = self.get_record_length()  # if no length is given, read in whole record length
        self.set_transfer_end_sample(end_sample)
