import serial
import time
import threading

class HardwareInterface():

    def __init__(self, port_name, b_rate, duration=0, delegate=None) -> None:
        self.daq_duration = duration
        self.daq_port_name = port_name
        self.callback_delegate = delegate
        self.baud_rate = b_rate
        self.daq_port = None
        self.force_stop = False
        self.worker_thread = None

    def open_port(self):
        if self.daq_port == None:
            self.daq_port = serial.Serial(self.daq_port_name, self.baud_rate)
            return
        if self.daq_port.is_open:
            return
        self.daq_port.open()

    def close_port(self):
        pass

    def start_reading(self):
        if self.daq_port == None or not self.daq_port.is_open:
            return
        def reading_worker():
            stop_condition = False
            if self.daq_duration <= 0:
                stop_condition = True
            end_stamp = time.time() + self.daq_duration
            while ((end_stamp >= time.time()) or stop_condition) and not self.force_stop:
                self.callback_delegate(self.daq_port.readline().decode())
        self.worker_thread = threading.Thread(target=reading_worker)
        self.worker_thread.start()

    def stop_reading(self, stop_thread=False):
        self.force_stop = True
        if stop_thread:
            pass
    
    def read_single(self):
        if self.daq_port == None or not self.daq_port.is_open:
            return None
        return self.daq_port.readline().decode()