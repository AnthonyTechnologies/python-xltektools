""" hdf5xltek.py
A HDF5 file which contains data for XLTEK EEG data.
"""
# Package Header #
from ..header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #

# Third-Party Packages #
from classversioning import Version, TriNumberVersion
from dspobjects.time import Timestamp

# Local Packages #
from .hdf5xltek import HDF5XLTEK


# Definitions #
# Classes #
class HDF5XLTEK_1(HDF5XLTEK):
    """A HDF5 file which contains data for XLTEK EEG data.

    Class Attributes:
        _registration: Determines if this class will be included in class registry.
        _VERSION_TYPE: The type of versioning to use.
        FILE_TYPE: The file type name of this class.
        VERSION: The version of this class.
        default_map: The HDF5 map of this object.
    """
    VERSION: Version = TriNumberVersion(1, 0, 0)

    @property
    def end_datetime(self) -> Timestamp | None:
        """The end datetime of this file."""
        return self["data"].components["timeseries"].get_datetime(-1)

    @property
    def end_nanostamp(self) -> float | None:
        """The end timestamp of this file."""
        return self["data"].components["timeseries"].get_nanostamp(-1)

    @property
    def end_timestamp(self) -> float | None:
        """The end timestamp of this file."""
        return self["data"].components["timeseries"].get_timestamp(-1)
