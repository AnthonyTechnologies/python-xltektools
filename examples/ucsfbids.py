""" ucsfbids.py.py

"""
# Header #
__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]

# Imports #
# Standard Libraries
import datetime
import pathlib

# Third-Party Packages
from ucsfbids import Subject, Session
import xltektools  # Ensures that the IEEGXLTEK class is added to the modularbids registry

# Setup #
server_path = pathlib.Path("/data_store0/human/converted_clinical")

start_time = datetime.datetime(1970, 1, 6, 0, 0, tzinfo=datetime.timezone.utc)  # Start Date is shifted to 1970
stop_time = datetime.datetime(1970, 1, 6, 0, 1, tzinfo=datetime.timezone.utc)

channels = slice(50, 100)  # Selects channels 50-99

# Load Session
bids_subject = Subject(name="EC0212", parent_path=server_path)
session = bids_subject.sessions["clinicalintracranial"]  # The recording name
cdfs = session.modalities["ieeg"].require_cdfs(load=True)  # Get the data loading object

# Get data
found_data = cdfs.data.find_data_slice(start_time, stop_time, approx=True)
new_channel = found_data[0].data[:, channels]
