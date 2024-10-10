#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" dash_example.py

"""
# Header #
__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]

# Imports #
# Standard Libraries
import datetime
import pathlib

# Third-Party Packages
from dash import Dash, html, dcc, Input, Output, callback
from dspobjects.plot import TimeSeriesPlot, HeatmapPlot, Figure
import numpy as np
from ucsfbids import Subject


# Definitions #
figure = Figure()
plot = TimeSeriesPlot(sample_rate=1024)


app = Dash(__name__)
app.layout = html.Div(
    html.Div([
        dcc.Graph(id='live-graph', figure=figure),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ])
)


def create_update_callback(streamer):
    @callback(Output('live-graph', 'extendData'), Input('graph-update', 'n_intervals'))
    def update_data(n):
        try:
            data = next(streamer)
        except StopIteration:
            pass
        else:
            return dict(x=[data[0]], y=[data[1]]), [0], 10


# Main #
if __name__ == "__main__":
    # Setup #
    path = pathlib.Path("//JasperNAS/root_store/subjects/sub-EC0197")
    update_interval = 1 # Update every 0.5 seconds

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
    stop_time = start_time + datetime.timedelta(hours=1)

    print("Create Datastreamer")
    streamer = proxy.find_data_islice_time(
            start=start_time,
            stop=stop_time,
            step=10,
            istep=update_interval,
            approx=True,
            tails=True,
        )

    print("Plotting Data")
    # plot = TimeSeriesPlot(y=data[:, 10:], sample_rate=1024)
    # plot._figure.show()

    create_update_callback(streamer)

    app.run_server(debug=False, host="0.0.0.0")
