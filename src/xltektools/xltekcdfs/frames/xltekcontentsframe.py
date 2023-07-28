"""xltekdatacontentsframe.py

"""
# Package Header #
from xltektools.header import *


# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import pathlib
from typing import Any

# Third-Party Packages #
from cdfs.contentsfile import TimeContentsLeafContainerInterface, TimeContentsNodeFrame, TimeContentsFrame

# Local Packages #
from ...hdf5xltek import HDF5XLTEK


# Definitions #
# Classes #
class XLTEKContentsLeafContainer(TimeContentsLeafContainerInterface):
    file_type: type[HDF5XLTEK] | None = HDF5XLTEK

    # Class Methods #
    @classmethod
    def validate_path(cls, path: pathlib.Path | str) -> bool:
        """Validates if path to the file exists and is usable.

        Args:
            path: The path to the file to validate.

        Returns:
            Whether this path is valid or not.
        """
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        if path.is_file():
            return cls.file_type.validate_file_type(path)
        else:
            return False

    # Instance Methods #
    def _is_open(self) -> bool:
        if self._file is not None:
            return bool(self._file)
        else:
            return False

    def load(self) -> None:
        """Loads the file's information into memory."""
        self._data = self.file["data"]
        self._time_axis = self._data.components["time_axis"]

    # Getters and Setters
    def get_data(self) -> Any:
        """Gets the data.

        Returns:
            The data object.
        """
        return self.file["data"]

    def set_data(self, value: Any) -> None:
        """Sets the data.

        Args:
            value: A data object.
        """
        if self.mode == "r":
            raise IOError("not writable")

    def get_time_axis(self) -> Any:
        """Gets the time axis.

        Returns:
            The time axis object.
        """
        return self.file["data"].components["time_axis"]

    def set_time_axis(self, value: Any) -> None:
        """Sets the time axis

        Args:
            value: A time axis object.
        """
        if self.mode == "r":
            raise IOError("not writable")


class XLTEKContentsNodeFrame(TimeContentsNodeFrame):
    default_node_type: type = None
    default_leaf_type: type = XLTEKContentsLeafContainer


class XLTEKContentsFrame(XLTEKContentsNodeFrame, TimeContentsFrame):
    default_node_type: type = XLTEKContentsNodeFrame


# Assign Cyclic Definition
XLTEKContentsNodeFrame.default_node_type = XLTEKContentsNodeFrame

