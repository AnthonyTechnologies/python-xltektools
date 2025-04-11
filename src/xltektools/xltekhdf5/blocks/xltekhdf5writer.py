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
        return {
            "file": {"file": full_path, "s_id": subject_id},
            "write": {"method": method} | (method_kwargs or {}),
            "data": {
                "update_id": update_id,
                "path": relative_path,
                "shape": shape,
                "axis": axis,
                "tz_offset": tz,
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
        axis: int = 0,
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

        # Set Metadata (Attributes cannot be written or read after file is in SWMR mode)
        self.file.time_axis.components["axis"].set_time_zone(timezone)
        self.file.time_axis.components["axis"].sample_rate = sample_rate
        self.file.attributes["start_id"] = start_id

        # Update Stored File Kwargs
        self.file_kwargs.clear()
        self.file_kwargs.update({"axis": axis} | file_kwargs)

        # Set Single Write Multiple Read
        self.file.swmr_mode = True

        # Clear Stored File Info
        self.data_info.clear()

    # Writing
    def set_data_slice(self, data, nanostamps, slice_: slice, axis: int = 0) -> None:
        # Get File's Dataset
        dataset = self.file.data
        time_axis = self.file.time_axis

        # Get Slicing
        file_shape = dataset.shape
        n_samples = file_shape[axis]
        data_shape = data.shape
        d_slicing = list(slice(d) for d in data_shape)
        d_slicing[axis] = slice_
        d_slicing = tuple(d_slicing)

        # Resize Data if needed
        new_time_shape = (n_sample if slice_ is None or slice_.stop is None else max(n_samples, slice_.stop),)
        new_data_shape = list(max(f, d) for f, d in zip(file_shape, data_shape))
        new_data_shape[axis] = new_time_shape[0]
        if tuple(new_data_shape) != file_shape:
            dataset.resize(new_data_shape)
            if new_time_shape[0] > time_axis.shape[0]:
                time_axis.resize(new_time_shape)

        # Update Data
        time_axis[slice_] = nanostamps
        dataset[d_slicing] = data
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

    # IO
    def build_io(self, *args: Any, override: bool = False, **kwargs: Any) -> None:
        """Builds the IO with the default settings and routing.

        Args:
            *args: Positional arguments for creating the IO.
            override: Determines if the IO will be overridden.
            **kwargs: Keyword arguments for creating the IO.
        """
        # Todo: Determine if the CallbackIOWrapper should also be StaticWrapper to allow method calls
        self.inputs.io_objects["write_packet"].wrapped.set_maxsize(3)

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
        write_info = info.pop("write")
        data_info = info.pop("data")

        # Change File if File Kwargs do not Match
        if file_kwargs["file"] != self.file_kwargs["file"]:
            self.change_file(
                data_info["start_id"],
                data_info["sample_rate"],
                data_info["tz_offset"],
                axis=data_info["axis"],
                file_kwargs=file_kwargs,
            )

        # Update File Info
        self.data_info.update(data_info)

        # Write Data
        method = getattr(self, write_info.pop("method"))  # Choose the data write method from string
        method(data, nanostamps, **({"axis": self.file_kwargs["axis"]} | write_info))

        # Return File Info
        return self.data_info.copy()

    # Teardown
    async def teardown(self, *args: Any, **kwargs: Any) -> None:
        """Tears down this block."""
        if self.file is not None:
            self.file.close()

        await self.outputs.put_item_async(self.signal_io_name, {"done_flag": True})
