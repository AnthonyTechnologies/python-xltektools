""" xltekdatacontentframe.py

"""
# Package Header #
from ...header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #

# Third-Party Packages #
from cdfs.contentsfile import TimeContentFrame

# Local Packages #
from .hdf5xltekframe import HDF5XLTEKFrame


# Definitions #
# Classes #
class XLTEKDataContentFrame(TimeContentFrame):
    default_frame_type = HDF5XLTEKFrame


# Assign Cyclic Definitions
XLTEKDataContentFrame.default_node_frame_type = XLTEKDataContentFrame
