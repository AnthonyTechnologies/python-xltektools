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
from ucsfbids import Subject


# Load Session
print("Opening Subject")
root_path = pathlib.Path("/data_store0/human/converted_clinical")
subject = Subject(name="EC0212", parent_path=root_path)
session = subject.sessions["clinicalintracranial"]  # The recording name
ieeg = session.modalities["ieeg"]  # The modality name

# Get Montage
print("Loading Montage")
montage = ieeg.load_electrodes()
labels = montage["name"]

# Get data
print("Accessing Data")
cdfs = ieeg.componenets["cdfs"].get_cdfs()  # Get the data loading object
proxy = cdfs.components["contents"].create_contents_proxy()

print("Selecting Time")
subject_start = proxy.start_datetime
start_time = subject_start + datetime.timedelta(days=1)
stop_time = subject_start + datetime.timedelta(minutes=1)

print("Fetching Data")
found_data = proxy.find_data_slice(start_time, stop_time, approx=True)

print("Plotting Data")
channels = slice(50, 100)  # Selects channels 50-99
data = found_data[0].data[:, channels]
