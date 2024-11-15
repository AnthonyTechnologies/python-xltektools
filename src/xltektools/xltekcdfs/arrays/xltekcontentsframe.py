"""xltekdatacontentsframe.py

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
from pathlib import Path
from typing import Any

# Third-Party Packages #
from cdfs.arrays import BaseTimeContentsLeafContainer, TimeContentsNodeProxy, TimeContentsProxy

# Local Packages #
from ...xltekhdf5 import XLTEKHDF5


# Definitions #
# Classes #
class XLTEKContentsLeafContainer(BaseTimeContentsLeafContainer):
    default_remain_open: bool = True
    file_type: type[XLTEKHDF5] | None = XLTEKHDF5

    # Class Methods #
    @classmethod
    def validate_path(cls, path: Path | str) -> bool:
        """Validates if path to the file exists and is usable.

        Args:
            path: The path to the file to validate.

        Returns:
            Whether this path is valid or not.
        """
        if not isinstance(path, Path):
            path = Path(path)

        if path.is_file():
            return cls.file_type.validate_file_type(path)
        else:
            return False

    # Instance Methods #
    @property
    def file(self) -> Path:
        """The file object."""
        if self._file is None:
            self._file = self.file_type(self._path, mode=self.mode, open_=self.remain_open, **self.file_kwargs)
        return self._file

    @file.setter
    def file(self, value: str | Path) -> None:
        self.set_file(value)

    def _is_open(self) -> bool:
        if self._file is not None:
            return bool(self._file)
        else:
            return False

    def load(self) -> None:
        """Loads the file's information into memory."""
        self._data = self.file["data"]
        self._time_axis = self._data.components["timeseries"].time_axis

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
        return self.file["data"].components["timeseries"].time_axis

    def set_time_axis(self, value: Any) -> None:
        """Sets the time axis

        Args:
            value: A time axis object.
        """
        if self.mode == "r":
            raise IOError("not writable")


class XLTEKContentsNodeProxy(TimeContentsNodeProxy):
    node_type: type = None
    leaf_type: type = XLTEKContentsLeafContainer


class XLTEKContentsProxy(XLTEKContentsNodeProxy, TimeContentsProxy):
    node_type: type = XLTEKContentsNodeProxy


# Assign Cyclic Definition
XLTEKContentsNodeProxy.node_type = XLTEKContentsNodeProxy
