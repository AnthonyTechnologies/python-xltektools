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

from select import select
# Third-Party Packages
from mxbids import Subject
import numpy as np

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure, show


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

source = ColumnDataSource(data=dict(x=np.arange(data.shape[0]), y=data[:, 0]))

p = figure(
    height=300, width=800, title="Voltage vs Time", tools="xpan", toolbar_location=None,
)
p.line(x="x", y="y", source=source)
p.yaxis.axis_label = "Voltage (uV)"
p.xaxis.axis_label = "Time (s)"

range_tool = RangeTool(x_range=p.x_range, start_gesture="pan")
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

selector = figure(
    height=50, width=800, x_axis_type="datetime", y_axis_type=None, tools="", toolbar_location=None
)
selector.line("x", "y", source=source)
selector.ygrid.grid_line_color = None
selector.add_tools(range_tool)

show(column(p, selector))
