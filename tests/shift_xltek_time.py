""" test_hdf5xltek.py

"""
# Package Header #
from src.xltektools.header import *


# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import datetime
import pathlib
import timeit

import numpy as np

# Third-Party Packages #
import pytest

# Local Packages #
from src.xltektools.hdf5framestructure import *


# Definitions #
FILE_DIR = pathlib.Path("/home/anthonyfong/ProjectData/EC133")
FILE_PATHS = FILE_DIR.glob("*.h5")
OUT_DIR = pathlib.Path("/home/anthonyfong/ProjectData/")
FILE_OUT = OUT_DIR.joinpath("EC133.h5")

start_date = datetime.date(2016, 9, 12)
delta_date = start_date - datetime.date(2016, 1, 1)

new_dt = []
data = []
for f_path in FILE_PATHS:
    with HDF5XLTEK(file=f_path, mode="a", create=False, load=True) as f_obj:
        time_axis = f_obj.time_axis
        new_dt.extend((dt - delta_date for dt in time_axis.datetimes))

        data.append(f_obj.data[:, 0:128])

new_data = np.concatenate(data, axis=0)

with HDF5XLTEK(file=FILE_OUT, mode="a", create=False, load=True) as f_obj:
    time_axis = f_obj.time_axis
    time_axis.from_datetimes(new_dt)

    f_obj.data.replace_data(new_data)
    f_obj.standardize_attributes()
