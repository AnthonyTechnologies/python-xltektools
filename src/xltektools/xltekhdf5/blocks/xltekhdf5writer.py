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
from datetime import datetime, tzinfo
from pathlib import Path
from typing import Any, ClassVar

# Third-Party Packages #
from blockobjects import BaseBlock
from dspobjects.time import Timestamp, nanostamp
import numpy as np

# Local Packages #
from ..xltekhdf5 import XLTEKHDF5


# Definitions #
# Classes #
class XLTEKHDF5Writer(BaseBlock):
    """A block which writes information to an XLTEKHDF5 file.

    Class Attributes:
        default_input_names: The default ordered tuple with the names of the inputs.
        default_output_names: The default ordered tuple with the names of the outputs.
        init_setup: Determines if the setup will occur during initialization.

    Attributes:
        file_type: Specifies the latest class version for XLTEKHDF5 type.
        file: A reference to the current XLTEKHDF5 file being written.
        file_kwargs: Keyword arguments related to file creation and handling.
    """

    # Class Attributes #
    default_input_names: ClassVar[tuple[str, ...]] = ("write_packet",)
    default_output_names: ClassVar[tuple[str, ...]] = ("entry",)
    init_setup: ClassVar[bool] = False

    # Class Methods #
    @classmethod
    def create_write_packet_info(
        cls,
        subject_id: str = "",
        full_path: str = "",
        relative_path: str = "",
        method: str = "",
        shape: tuple[int, ...] = (),
        sample_rate: int | float | None = None,
        start: datetime | float | int | np.dtype | np.ndarray | None = None,
        end: datetime | float | int | np.dtype | np.ndarray | None = None,
        tz: tzinfo = None,
        start_id: int | None = None,
        end_id: int | None = None,
        axis: int = 0,
        update_id: int = 0,
        method_kwargs: dict[str, Any] | None = None,
    ) -> dict:
        if not isinstance(start, Timestamp):
            start = Timestamp(start, tz=tz)

        if end is None:
            end = start
        elif not isinstance(end, Timestamp):
            end = Timestamp(end, tz=tz)

        return {
            "file": {"file": full_path, "s_id": subject_id},
            "write": {"method": method} | (method_kwargs or {}),
            "data": {
                "update_id": update_id,
                "path": relative_path,
                "shape": shape,
                "axis": axis,
                "timezone": tzinfo,
                "start": start,
                "end": end,
                "sample_rate": sample_rate,
                "start_id": int(nanostamp(start)) if start_id is None and start is not None else start_id,
                "end_id": int(nanostamp(end)) if end_id is None and end is not None else end_id,
            },
        }

    # Attributes #
    file_type: type[XLTEKHDF5] = XLTEKHDF5.get_latest_version_class()

    file_kwargs: dict[str, Any] = {"file": ""}
    data_info: dict[str, Any] = {}

    file: XLTEKHDF5 | None = None

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        file: XLTEKHDF5 | None = None,
        file_type: type[XLTEKHDF5] = None,
        *args: Any,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #

        # Parent Attributes #
        super().__init__(init=False)

        # Construct #
        if init:
            self.construct(file, file_type, *args, **kwargs)

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        file: XLTEKHDF5 | None = None,
        file_type: type[XLTEKHDF5] = None,
        *args: Any,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Assign Attributes #
        if file is not None:
            self.file = file

        if file_type is not None:
            self.file_type = file_type

        # Construct Parent #
        super().construct(*args, **kwargs)

    # File
    def change_file(
        self,
        start_id,
        sample_rate,
        timezone,
        *args: Any,
        file_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        # Close Previous File
        if self.file is not None:
            self.file.close()

        # Open File
        match file_kwargs:
            case {"remake": True, "file": file_path}:
                Path(file_path).unlink()
                del file_kwargs["remake"]
            case {"remake": False, "file": file_path}:
                del file_kwargs["remake"]

        self.file = self.file_type(**({"mode": "w", "create": True, "construct": True} | (file_kwargs or {})))

        # Set Metadata
        self.file.time_axis.components["axis"].set_time_zone(timezone)
        self.file.time_axis.components["axis"].sample_rate = sample_rate
        self.file.attributes["start_id"] = start_id

        # Set Single Write Multiple Read
        self.file.swmr_mode = True

        # Update Stored File Kwargs
        self.file_kwargs.clear()
        self.file_kwargs.update(file_kwargs)

        # Clear Stored File Info
        self.data_info.clear()

    # Writing
    def set_data_slice(self, data, nanostamps, slice_: slice, axis: int | None = None) -> None:
        # Get File's Dataset
        dataset = self.file.data
        time_axis = dataset.components["timeseries"].time_axis

        # Get Slicing
        if axis is None:
            axis = dataset.components["timeseries"].t_axis

        file_shape = dataset.shape
        n_samples = file_shape[axis]
        d_slicing = [slice(None)] * len(file_shape)
        d_slicing[axis] = slice(dataset.shape[0], data.shape[0])
        d_slicing = tuple(d_slicing)

        # Resize Data if needed
        start = 0 if slice_ is None else slice_.start
        stop = n_samples if slice_ is None else slice_.stop
        if start > n_samples or stop > n_samples:
            new_shape = list(file_shape)
            new_shape[axis] = stop
            dataset.reize(new_shape)
            t_shape = list(time_axis.shape)
            t_shape[axis] = n_samples
            time_axis.reize(t_shape)

        # Update Data
        dataset[d_slicing] = data[d_slicing]
        time_axis[slice_] = nanostamps
        self.file.flush()
        self.data_info["shape"] = dataset.shape

    def append_data(self, data, nanostamps) -> None:
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

    # Setup
    def setup(self, *args: Any, **kwargs: Any) -> None:
        """Sets up this block."""
        self.file_kwargs = self.file_kwargs.copy()
        self.data_info = self.data_info.copy()

    # Evaluate
    def evaluate(self, write_packet: tuple, *args: Any, **kwargs: Any) -> Any:
        """Writes information to an XLTEKHDF5 file.

        Args:
            write_packet: The information to write to a file.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            An entry to insert into an XLTEKCDFS contents table.
        """
        # Separate Write Information
        info, data, nanostamps = write_packet
        file_kwargs = info.pop("file")
        write_info = info.pop("write_info")
        data_info = info.pop("data_info")

        # Change File if File Kwargs do not Match
        if file_kwargs["file"] != self.file_kwargs["file"]:
            self.change_file(
                data_info["start_id"],
                data_info["sample_rate"],
                data_info["timezone"],
                file_kwargs=file_kwargs,
            )

        # Update File Info
        self.data_info.update(data_info)

        # Write Data
        method = getattr(self, write_info.pop("method"))  # Choose the data write method from string
        method(data, nanostamps, **data_info)

        # Return File Info
        return self.data_info.copy()

    # Teardown
    async def teardown(self, *args: Any, **kwargs: Any) -> None:
        """Tears down this block."""
        if self.file is not None:
            self.file.close()

        await self.outputs.put_item_async(self.signal_io_name, {"done_flag": True})
