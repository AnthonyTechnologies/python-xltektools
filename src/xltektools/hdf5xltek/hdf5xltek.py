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
from classversioning import VersionType, Version, TriNumberVersion
from hdf5objects.hdf5bases import HDF5Map
from hdf5objects.dataset import BaseTimeSeriesMap
from hdf5objects.fileobjects import HDF5EEG, HDF5EEGMap

# Local Packages #


# Definitions #
# Classes #
class HDF5XLTEKMap(HDF5EEGMap):
    """A map for HDF5XLTEK files."""
    default_attributes = HDF5EEGMap.default_attributes | {"age": "", "sex": "U", "species": "Homo Sapien"}
    default_map_names = {"data": "ECoG"}
    default_maps = {"data": BaseTimeSeriesMap()}


class HDF5XLTEK(HDF5EEG):
    """A HDF5 file which contains data for XLTEK EEG data.

    Class Attributes:
        _registration: Determines if this class will be included in class registry.
        _VERSION_TYPE: The type of versioning to use.
        FILE_TYPE: The file type name of this class.
        VERSION: The version of this class.
        default_map: The HDF5 map of this object.
    """
    _registration: bool = True
    _VERSION_TYPE: VersionType = VersionType(name="HDF5XLTEK", class_=TriNumberVersion)
    VERSION: Version = TriNumberVersion(0, 0, 0)
    FILE_TYPE: str = "XLTEK_EEG"
    default_map: HDF5Map = HDF5XLTEKMap()
