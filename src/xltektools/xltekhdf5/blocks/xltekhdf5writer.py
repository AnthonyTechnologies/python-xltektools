""" xltekhdf5writer.py
A block which writes information to an XLTEKHDF5 file.
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
from typing import Any, ClassVar

# Third-Party Packages #
from dspobjects.time import Timestamp
from blockobjects import BaseBlock

# Local Packages #
from ..xltekhdf5 import XLTEKHDF5


# Definitions #
# Classes #
class XLTEKHDF5Writer(BaseBlock):
    """A block which writes information to an XLTEKHDF5 file.

    Class Attributes:
        default_input_names: The default ordered tuple with the names of the inputs.
        init_setup: Determines if the setup will occur during initialization.

    Attributes:
        file_type: Specifies the latest class version for XLTEKHDF5 type.
        file: A reference to the current XLTEKHDF5 file being written.
        file_kwargs: Keyword arguments related to file creation and handling.
    """

    # Class Attributes #
    default_input_names: ClassVar[tuple[str, ...]] = ("write_info",)
    init_setup: ClassVar[bool] = False

    # Attributes #
    file_type: type[XLTEKHDF5] = XLTEKHDF5.get_latest_version_class()

    file: XLTEKHDF5 | None = None
    file_kwargs: dict[str, Any] | None = None

    # Instance Methods #
    # Setup
    def setup(self, *args: Any, **kwargs: Any) -> None:
        """Sets up this block."""
        if self.file_kwargs is None:
            self.file_kwargs = {"file": ""}

    # Evaluate
    def evaluate(self, write_info: tuple, *args: Any, **kwargs: Any) -> Any:
        """Writes information to an XLTEKHDF5 file.

        Args:
            write_info: The information to write to a file.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            An entry to insert into an XLTEKCDFS contents table.
        """
        # Separate Write Information
        info, data, nanostamps = write_info
        file_kwargs = info.pop("file")

        # Create New File if File Kwargs do not Match
        if file_kwargs["file"] != self.file_kwargs["file"]:
            # Close Previous File
            if self.file is not None:
                self.file.close()

            # Open File
            try:
                self.file = self.file_type(mode="a", create=True, construct=True, **file_kwargs)
            except OSError:
                # If there is a corrupt file, delete it, and create a new file.
                file_kwargs["file"].unlink(missing_ok=True)
                self.file = self.file_type(mode="a", create=True, construct=True, **file_kwargs)

            # Set Metadata
            self.file.time_axis.components["axis"].set_time_zone(info["contents_insert"]["timezone"])
            self.file.time_axis.components["axis"].sample_rate = info["contents_insert"]["sample_rate"]
            self.file.attributes["start_id"] = info["contents_insert"]["start_id"]

            # Set Single Write Multiple Read
            self.file.swmr_mode = True

            # Update Stored File Kwargs
            self.file_kwargs.clear()
            self.file_kwargs.update(file_kwargs)

        # Get File's Dataset
        dataset = self.file.data

        # Get Slicing
        d_slicing = [slice(None, i) for i in data.shape]
        d_slicing[0] = slice(dataset.shape[0], data.shape[0])
        d_slicing = tuple(d_slicing)
        n_slicing = slice(self.file.time_axis.shape[0], data.shape[0])

        # Update Data
        dataset.append(data[d_slicing], component_kwargs={"timeseries": {"data": nanostamps[n_slicing]}})
        self.file.flush()

        return info["contents_insert"]

    # Teardown
    def teardown(self, *args: Any, **kwargs: Any) -> None:
        """Tears down this block."""
        if self.file is not None:
            self.file.close()
