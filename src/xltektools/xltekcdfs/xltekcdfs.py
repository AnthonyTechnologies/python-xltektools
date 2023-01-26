""" xltekcdfs.py

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
from typing import Any
from datetime import datetime
from decimal import Decimal
import pathlib
import uuid

# Third-Party Packages #
from cdfs import CDFS
from hdf5objects import HDF5Map
import numpy as np

# Local Packages #
from ..hdf5xltek import HDF5XLTEK
from .contentsfile import XLTEKContentsFile
from .frames import XLTEKDataContentFrame


# Definitions #
# Classes #
class XLTEKCDFS(CDFS):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    default_component_types: dict[str, tuple[type, dict[str, Any]]] = {}
    default_frame_type = XLTEKDataContentFrame
    default_data_file_type: type = HDF5XLTEK.get_latest_version_class()
    contents_file_type: type = XLTEKContentsFile

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: pathlib.Path | str | None = None,
        s_id: str | None = None,
        s_dir: pathlib.Path | None = None,
        mode: str = 'r',
        update: bool = False,
        open_: bool = True,
        load: bool = True,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.subject_id: str | None = None
        self._subjects_dir: pathlib.Path | None = None

        self.date_format: str = "%d"
        self.time_format: str = "%d_%h~%m~%s"

        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(
                path=path,
                s_id=s_id,
                s_dir=s_dir,
                mode=mode,
                update=update,
                load=load,
                open_=open_,
                **kwargs,
            )

    @property
    def subjects_dir(self) -> pathlib.Path:
        """The path to the CDFS."""
        return self._subjects_dir

    @subjects_dir.setter
    def subjects_dir(self, value: str | pathlib.Path) -> None:
        if isinstance(value, pathlib.Path) or value is None:
            self._subjects_dir = value
        else:
            self._subjects_dir = pathlib.Path(value)

    # Instance Methods
    # Constructors/Destructors
    def construct(
        self,
        path: pathlib.Path | str | None = None,
        s_id: str | None = None,
        s_dir: pathlib.Path | None = None,
        mode: str = 'r',
        update: bool = False,
        open_: bool = False,
        load: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            path: The path for this frame to wrap.
            s_id: The subject ID.
            studies_path: The parent directory to this XLTEK study frame.
            frames: An iterable holding frames/objects to store in this frame.
            mode: Determines if the contents of this frame are editable or not.
            update: Determines if this frame will start_timestamp updating or not.
            open_: Determines if the frames will remain open after construction.
            load: Determines if the frames will be constructed.
            **kwargs: The keyword arguments to create contained frames.
        """
        if s_id is not None:
            self.subject_id = s_id

        if s_dir is not None:
            self.subjects_dir = s_dir

        if path is None and self.path is None and self.subject_id is not None and self.subjects_dir is not None:
            self.path = self.subjects_dir / self.subject_id

        super().construct(path=path, mode=mode, update=update, open_=open_, load=load, **kwargs)

    def create_day(
        self,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        name: str | None = None,
        sample_rate: float | str | Decimal | None = None,
        length: int = 0,
        min_shape: tuple[int] = (),
        max_shape: tuple[int] = (),
        id_: str | uuid.UUID | None = None,
    ) -> None:
        if name is None:
            name = f"{self.subject_id}_{start.date().strftime(self.date_format)}"

        day_path = self.path / name
        day_path.mkdir()

        self.contents_file["data_content"].components["xltek_data"].create_day(
            path=name,
            length=length,
            start=start,
            end=end,
            min_shape=min_shape,
            max_shape=max_shape,
            sample_rate=sample_rate,
            id_=id_,
        )

    def generate_file_name(self, start: datetime):
        return f"{self.subject_id}_{start.strftime(self.time_format)}"

    def add_file(self, file: HDF5XLTEK):
        self.contents_file["data_content"].components["xltek_data"].insert_entry_start(
            path=file.path.name,
            start=file.start_datetime,
            end=file.end_datetime,
            length=len(file.time_axis),
            min_shape=file.data.shape,
            max_shape=file.data.shape,
            sample_rate=file.sample_rate,
            day_path=file.path.parts[-2],
        )
