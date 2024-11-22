#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" xltek_bids.py

"""
# Header #
__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]

# Imports #
# Standard Libraries
import datetime
import pathlib
import sys

# Third-Party Packages
import PySide6
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import QTimer, Qt
import pyqtgraph as pg
import numpy as np
from mxbids import Subject


# Definitions #
class MainWindow(QWidget):
    def __init__(self, streamer, channels, scale=1.1, offset=250.0):
        super().__init__()
        self.streamer = streamer

        self.setWindowTitle("Data Fetching Example")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Timer set to 0.5 second (500 ms)

        self.plot_widget = pg.PlotWidget(title="Time Series Plot")

        if isinstance(channels, int):
            self.channels = slice(channels)
            self.n_channels = channels
        if isinstance(channels, slice):
            self.channels = channels
            self.n_channels = channels.stop - channels.start
        else:
            self.channels = channels
            self.n_channels = len(channels)

        self.scale = scale
        self.traces = [None] * self.n_channels
        for i in range(self.n_channels):
            self.traces[i] = self.plot_widget.plot(pen=(i, 10))

        self.offsets = np.expand_dims(np.arange(self.n_channels) * offset, axis=0)

        self.layout = PySide6.QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.plot_widget)

    def update_plot(self):
        try:
            data = next(self.streamer)[:, self.channels] * self.scale
        except StopIteration:
            self.timer.stop()
        else:
            data += np.repeat(self.offsets, data.shape[0], axis=0)
            x = np.arange(data.shape[0])
            for i in range(len(self.traces)):
                self.traces[i].setData(x=x, y=data[:, i])


# Main #
if __name__ == "__main__":
    # Setup #
    path = pathlib.Path("//JasperNAS/root_store/updated_subjects/sub-EC0322")
    update_interval = 0.1  # Update every 0.5 seconds

    # Load Session
    print("Opening Subject")
    bids_subject = Subject(path=path, load=True)
    session = bids_subject.sessions["clinicalintracranial"]  # The recording name
    cdfs = session.modalities["ieeg"].components["cdfs"].get_cdfs()  # Get the data loading object

    # Get data
    print("Accessing Data")
    proxy = cdfs.components["contents"].create_contents_proxy()

    print("Selecting Time")
    subject_start = proxy.start_datetime
    start_time = (subject_start + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    stop_time = start_time + datetime.timedelta(minutes=10)

    print("Create Datastreamer")
    streamer = proxy.find_data_islice_time(
        start=start_time,
        stop=stop_time,
        step=10.0,
        istep=update_interval/10,
        approx=True,
        tails=True,
    )

    print("Plotting Data")
    app = QApplication(sys.argv)
    window = MainWindow(streamer, slice(6, 79))
    window.show()
    sys.exit(app.exec())
