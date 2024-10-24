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

# Third-Party Packages
from dspobjects.plot import TimeSeriesPlot
from mxbids import Subject

# Setup #
path = pathlib.Path("//JasperNAS/root_store/temp_subjects/sub-EC0212")

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
start_time = (subject_start + datetime.timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
# start_time = subject_start + datetime.timedelta(minutes=1)
stop_time = start_time + datetime.timedelta(minutes=1)

print("Fetching Data")
found_data = proxy.find_data_slice(start_time, stop_time, approx=True)

print("Plotting Data")
channels = slice(0, 10)  # Selects channels 50-99
data = found_data[0].data[:, channels]
TimeSeriesPlot(y=data, sample_rate=found_data[0].sample_rate)._figure.show()
