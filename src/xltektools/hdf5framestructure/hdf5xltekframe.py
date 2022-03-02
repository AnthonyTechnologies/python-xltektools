""" hdf5xltekframe.py

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

# Local Packages #
from ..fileobjects import HDF5XLTEK
from .hdf5baseframe import HDF5BaseFrame


# Definitions #
# Classes #
class HDF5XLTEKFrame(HDF5BaseFrame):
    file_type: type = HDF5XLTEK
    default_data_container = None

    # Magic Methods
    # Construction/Destruction
    def __init__(self, file=None, s_id=None, s_dir=None, start=None, mode='r', init=True, **kwargs):
        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(file=file, s_id=s_id, s_dir=s_dir, start=start, mode=mode, **kwargs)

    # Instance Methods
    # Constructors/Destructors
    def construct(self, file=None, s_id=None, s_dir=None, start=None, mode=None, **kwargs):
        if mode is not None:
            self.mode = mode

        if file is not None:
            self.set_file(file, s_id=s_id, s_dir=s_dir, start=start, mode=self.mode, **kwargs)
        elif s_id is not None or s_dir is not None or start is not None or kwargs:
            self.file = self.file_type(s_id=s_id, s_dir=s_dir, start=start, mode=self.mode, **kwargs)

        super().construct(file=None)
