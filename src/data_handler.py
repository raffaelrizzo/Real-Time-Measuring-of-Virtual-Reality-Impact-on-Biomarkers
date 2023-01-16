import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt
from matplotlib.ticker import FuncFormatter
from scipy import signal
from pyampd.ampd import find_peaks
import hw_interface
import json


daq_duration = 60

data_entries = []
def store_data(data):
    data = json.loads(data)
    data_entries.append(data['v1'])

data_source = hw_interface.HardwareInterface('/dev/cu.usbmodem14101', 9600, daq_duration, store_data)
data_source.open_port()
data_source.start_reading()
time.sleep(daq_duration + 5)


data_entries = np.array(data_entries)
sample_freq = data_entries.shape[0] / daq_duration
sample_count = int(sample_freq) * daq_duration
data_entries = data_entries[:sample_count]

de_trended = signal.detrend(data_entries)

blp, alp = butter(5, 5, btype='low', fs=sample_freq, analog=False)
# bhp, ahp = butter(5, 0.5, btype='high', fs=sample_freq, analog=False)
raw_filtered = filtfilt(blp, alp, data_entries)
# raw_filtered = filtfilt(bhp, ahp, raw_filtered)
de_trended_filtered = filtfilt(blp, alp, de_trended)

plt.plot(data_entries[:sample_count], label='Amplified Signal')
plt.plot(de_trended, label='Detrended Signal')
plt.plot(raw_filtered, label='4Hz Low Pass')
plt.plot(de_trended_filtered, label='Detrended Filter')


plt.legend()
plt.xlabel('Time',fontsize=20)
plt.ylabel('Amplitude',fontsize=20)


peaks = find_peaks(de_trended_filtered, scale=100)

plt.plot(peaks, de_trended_filtered[peaks], 'x')

print(peaks.shape)

plt.show()