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
from decimal import Decimal

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

    def get_sample_rate(self) -> float | None:
        """Get the sample rate of this frame from the contained frames/objects.

        Returns:
            The sample rate of this frame.
        """
        sample_rate = self.get_sample_rate_decimal()
        return float(sample_rate) if sample_rate is not None else None

    def get_sample_rate_decimal(self) -> Decimal | None:
        """Get the sample rate of this frame from the contained frames/objects.

        Returns:
            The shape of this frame or the minimum sample rate of the contained frames/objects.
        """
        sample_rate = self.time_axis.get_sample_rate_decimal()
        if sample_rate is None:
            try:
                sample_rate = Decimal(self.data.attributes.get_attribute("sample_rate"))
            except TypeError:
                return None

        return sample_rate

    def get_sample_period(self) -> float | None:
        """Get the sample period of this frame.

        If the contained frames/object are different this will raise a warning and return the maximum period.

        Returns:
            The sample period of this frame.
        """
        sample_rate = self.get_sample_rate_decimal()
        return 1 / float(sample_rate) if sample_rate is not None else None

    def get_sample_period_decimal(self) -> Decimal | None:
        """Get the sample period of this frame.

        If the contained frames/object are different this will raise a warning and return the maximum period.

        Returns:
            The sample period of this frame.
        """
        sample_rate = self.get_sample_rate_decimal()
        return 1 / sample_rate if sample_rate is not None else None
