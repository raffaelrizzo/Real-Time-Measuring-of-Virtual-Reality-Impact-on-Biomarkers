import serial
from random import randint
from PyQt5.QtCore import QDateTime, Qt, QTimer
import pyqtgraph as pg
from PyQt5 import QtCore
import numpy as np
from pyampd.ampd import find_peaks
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from scipy import signal
import json
import hw_interface

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.data_source = hw_interface.HardwareInterface('/dev/cu.usbmodem14101', 9600, 0)
        self.data_source.open_port()
        axis_length = 500
        self.heartGraph_x = list(range(axis_length))
        self.oxygenGraph_x = list(range(axis_length))
        self.glucoseGraph_x = list(range(axis_length))
        self.heartGraph_y = [0 for _ in range(axis_length)]
        initial_blood_oxygen = randint(94, 100)
        initial_blood_glucose = np.random.normal(5.5, .7)
        self.oxygenGraph_y = [initial_blood_oxygen for _ in range(axis_length)]
        self.glucoseGraph_y = [initial_blood_glucose for _ in range(axis_length)]

        self.heart_beat_mean = 61

        self.beat_rate_cache = [0 for _ in range(50)]

        mainLayout = QGridLayout()
        self.setLayout(mainLayout)
        self.setGeometry(250, 250, 750, 750)

        self.heartGraph = pg.PlotWidget()
        self.oxygenGraph = pg.PlotWidget()
        self.glucoseGraph = pg.PlotWidget()
        mainLayout.addWidget(self.heartGraph, 0, 0)
        mainLayout.addWidget(self.oxygenGraph, 1, 0)
        mainLayout.addWidget(self.glucoseGraph, 2, 0)


        self.heart_rate_label = QLabel()
        self.heart_rate_value_label = QLabel()
        self.heart_rate_label.setText('Heart Beat Rate: ')
        mainLayout.addWidget(self.heart_rate_label, 0, 1)
        mainLayout.addWidget(self.heart_rate_value_label, 0, 2)


        self.blood_oxygen_label = QLabel()
        self.blood_oxygen_value_label = QLabel()
        self.blood_oxygen_label.setText('Blood Oxygen: ')
        mainLayout.addWidget(self.blood_oxygen_label, 1, 1)
        mainLayout.addWidget(self.blood_oxygen_value_label, 1, 2)


        self.blood_glucose_label = QLabel()
        self.blood_glucose_value_label = QLabel()
        self.blood_glucose_label.setText('Blood Glucose: ')
        mainLayout.addWidget(self.blood_glucose_label, 2, 1)
        mainLayout.addWidget(self.blood_glucose_value_label, 2, 2)


        pen = pg.mkPen(color=(255, 0, 0))

        self.heart_beat_data_line =  self.heartGraph.plot(self.heartGraph_x, self.heartGraph_y, pen=pen)
        self.blood_oxygen_data_line =  self.oxygenGraph.plot(self.oxygenGraph_x, self.oxygenGraph_y, pen=pen)
        self.blood_glucose_data_line =  self.glucoseGraph.plot(self.glucoseGraph_x, self.glucoseGraph_y, pen=pen)
        
        self.heart_rate_timer = QtCore.QTimer()
        self.heart_rate_timer.setInterval(0)
        self.heart_rate_timer.timeout.connect(self.update_heart_beat)
        self.heart_rate_timer.start()

        self.blood_oxygen_timer = QtCore.QTimer()
        self.blood_oxygen_timer.setInterval(3000)
        self.blood_oxygen_timer.timeout.connect(self.update_blood_oxygen)
        self.blood_oxygen_timer.start()

        self.blood_glucose_timer = QtCore.QTimer()
        self.blood_glucose_timer.setInterval(3000)
        self.blood_glucose_timer.timeout.connect(self.update_blood_glucose)
        self.blood_glucose_timer.start()


    def update_heart_beat(self):
        data = self.data_source.read_single()
        data = json.loads(data)
        self.heartGraph_x = self.heartGraph_x[1:]
        self.heartGraph_x.append(self.heartGraph_x[-1] + 1)
        self.heartGraph_y = self.heartGraph_y[1:]
        if data['v1'] == None:
            self.heartGraph_y.append(0)
        else:
            self.heartGraph_y.append(data['v1'])
        self.beat_rate_cache = self.beat_rate_cache[1:]
        self.beat_rate_cache.append(np.random.normal(self.heart_beat_mean, 3))

        bhp, ahp = signal.butter(5, 1, btype='high', fs=180, analog=False)
        blp, alp = signal.butter(5, 5, btype='low', fs=180, analog=False)
        filtered_signal = signal.filtfilt(blp, alp, self.heartGraph_y).tolist()
        filtered_signal = signal.filtfilt(bhp, ahp, filtered_signal).tolist()
        peaks = find_peaks(filtered_signal, scale=100)
        
        self.heart_rate_value_label.setText(str(int(peaks.shape[0]*7)))
        self.heart_beat_data_line.setData(self.heartGraph_x, filtered_signal)

    def update_blood_oxygen(self):
        # data = self.arduino_serial.readline().decode()
        # data = json.loads(data)
        self.oxygenGraph_x = self.oxygenGraph_x[1:]
        self.oxygenGraph_x.append(self.oxygenGraph_x[-1] + 1)

        self.oxygenGraph_y = self.oxygenGraph_y[1:]
        # self.oxygenGraph_y.append(data['v1'])
        new_oxygen_datapoint = self.oxygenGraph_y[-1] + np.random.normal(0, 0.01)
        self.oxygenGraph_y.append(new_oxygen_datapoint)
        self.blood_oxygen_value_label.setText('{:02.0f}'.format(self.oxygenGraph_y[-1]))
        self.blood_oxygen_data_line.setData(self.oxygenGraph_x, self.oxygenGraph_y)

    def update_blood_glucose(self):
        # data = self.arduino_serial.readline().decode()
        # data = json.loads(data)
        self.glucoseGraph_x = self.glucoseGraph_x[1:]
        self.glucoseGraph_x.append(self.glucoseGraph_x[-1] + 1)

        self.glucoseGraph_y = self.glucoseGraph_y[1:]
        # self.glucoseGraph_y.append(data['v1'])
        new_glucose_datapoint = self.glucoseGraph_y[-1] + np.random.normal(0, 0.01)
        self.glucoseGraph_y.append(new_glucose_datapoint)
        self.blood_glucose_value_label.setText('{:03.2f}'.format(self.glucoseGraph_y[-1]))

        self.blood_glucose_data_line.setData(self.glucoseGraph_x, self.glucoseGraph_y)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec())