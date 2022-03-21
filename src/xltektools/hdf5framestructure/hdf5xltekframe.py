""" hdf5xltekframe.py
The frame for an HDF5 XLTEK File.
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
from hdf5objects.arrayframes import HDF5EEGFrame

# Local Packages #
from .hdf5xltek import HDF5XLTEK


# Definitions #
# Classes #
class HDF5XLTEKFrame(HDF5EEGFrame):
    """The frame for an HDF5 XLTEK File.

    Class Attributes:
        file_type: The type of file this object will be wrapping.
        default_data_container: The default data container to use when making new data container frames.
    """
    file_type: type = HDF5XLTEK
    default_data_container: type | None = None
