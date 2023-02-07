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
from datetime import datetime, date, timezone
from decimal import Decimal
import pathlib
import uuid

# Third-Party Packages #
from cdfs import CDFS
from dspobjects.time import Timestamp
from hdf5objects import HDF5Map
import numpy as np

# Local Packages #
from ..hdf5xltek import HDF5XLTEK
from .contentsfile import XLTEKContentsFile, XLTEKDataGroupComponent
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
        self._subjects_dir: pathlib.Path | None = None

        self._subject_id: str | None = None
        self._age: str | None = None
        self._sex: str | None = None
        self._species: str | None = None

        self.date_format: str = "%d"
        self.time_format: str = "%H~%M~%S"

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

    @property
    def subject_id(self) -> str | None:
        """The subject ID from the file attributes."""
        if self.contents_file is None or not self.contents_file.is_open:
            return self._subject_id
        else:
            return self.contents_file.attributes.get("subject_id", None)

    @subject_id.setter
    def subject_id(self, value: str) -> None:
        if self.contents_file is not None and not self.contents_file.is_open:
            self.contents_file.attributes.set_attribute("subject_id", value)
        self._subject_id = value

    @property
    def age(self) -> str | None:
        """The subject age from the file attributes."""
        if self.contents_file is None or not self.contents_file.is_open:
            return self._age
        else:
            return self.contents_file.attributes.get("age", None)

    @age.setter
    def age(self, value: str) -> None:
        if self.contents_file is not None and not self.contents_file.is_open:
            self.contents_file.attributes.set_attribute("age", value)
        self._age = value

    @property
    def sex(self) -> str | None:
        """The subject sex from the file attributes."""
        if self.contents_file is None or not self.contents_file.is_open:
            return self._sex
        else:
            return self.contents_file.attributes.get("sex", None)

    @sex.setter
    def sex(self, value: str) -> None:
        if self.contents_file is not None and not self.contents_file.is_open:
            self.contents_file.attributes.set_attribute("sex", value)
        self._sex = value

    @property
    def species(self) -> str | None:
        """The subject species from the file attributes."""
        if self.contents_file is None or not self.contents_file.is_open:
            return self._species
        else:
            return self.contents_file.attributes.get("species", None)

    @species.setter
    def species(self, value: str) -> None:
        if self.contents_file is not None and not self.contents_file.is_open:
            self.contents_file.attributes.set_attribute("species", value)
        self._species = value
    
    @property
    def xltek_data_group(self) -> XLTEKDataGroupComponent:
        return  self.contents_file.components["contents"].get_data_root()

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
            self._subject_id = s_id

        if s_dir is not None:
            self.subjects_dir = s_dir

        if path is None and self.path is None and self.subject_id is not None and self.subjects_dir is not None:
            self.path = self.subjects_dir / self.subject_id

        super().construct(path=path, mode=mode, update=update, open_=open_, load=load, **kwargs)
    
    def require(self, **kwargs):
        self.path.mkdir(exist_ok=True)

        if self.contents_file is None:
            self.construct_contents_file(create=True, require=True, **kwargs)
            self.construct_data()
        else:
            self.contents_file.require(**kwargs)
    
    def get_start_datetime(self):
        return self.xltek_data_group.get_start_datetime()

    def get_end_datetime(self):
        return self.xltek_data_group.get_end_datetime()

    def create_day(
        self,
        start: datetime | date | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        path: str | None = None,
        sample_rate: float | str | Decimal | None = None,
        length: int = 0,
        min_shape: tuple[int] = (),
        max_shape: tuple[int] = (),
        id_: str | uuid.UUID | None = None,
    ) -> None:
        if path is None:
            path = f"{self.subject_id}_{start.date().strftime(self.date_format)}"

        day_path = self.path / path
        day_path.mkdir()

        self.contents_file["data_content"].components["xltek_data"].create_day(
            start=start,
            end=end,
            path=name,
            length=length,
            min_shape=min_shape,
            max_shape=max_shape,
            sample_rate=sample_rate,
            id_=id_,
        )

    def require_day(
        self,
        start: datetime | date | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        path: str | None = None,
        sample_rate: float | str | Decimal | None = None,
        length: int = 0,
        min_shape: tuple[int] = (),
        max_shape: tuple[int] = (),
        id_: str | uuid.UUID | None = None,
    ) -> None:
        if path is None:
            path = f"{self.subject_id}_{start.date().strftime(self.date_format)}"

        day_path = self.path / path
        day_path.mkdir(exist_ok=True)

        day_dataset = self.xltek_data_group.require_day(
            start=start,
            end=end,
            path=name,
            length=length,
            min_shape=min_shape,
            max_shape=max_shape,
            sample_rate=sample_rate,
            id_=id_,
        )

        return day_path, day_dataset

    def generate_file_name(self, start: datetime):
        return f"{self.subject_id}_{start.strftime(self.time_format)}"

    def add_file(self, file: HDF5XLTEK):
        self.xltek_data_group.insert_entry_start(
            path=file.path.name,
            start=file.start_datetime,
            end=file.end_datetime,
            length=len(file.time_axis),
            min_shape=file.data.shape,
            max_shape=file.data.shape,
            sample_rate=file.sample_rate,
            day_path=file.path.parts[-2],
        )

    def create_file(self, data, sample_rate, nanostamps, tzinfo=None, open_=False):
        start = Timestamp.fromnanostamp(nanostamps[0], tz=timezone.utc)
        index, _ = self.xltek_data_group.find_child_index_start_day(start, approx=True, tails=True, sentinel=(0, None))

        day_name = f"{self.subject_id}_Day-{index + 1}"
        day_path = self.path / day_name
        day_path.mkdir(exist_ok=True)

        file_name = f"{day_name}_{start.strftime(self.time_format)}.h5"
        file_path = day_path / file_name
        if file_path.is_file():
            file_name = f"{day_name}_{start.strftime(f'{self.time_format}.%f')}.h5"
            file_path = day_path / file_name

        f_obj = self.data_file_type(
            file=file_path,
            s_id=self.subject_id,
            start=start,
            mode="a",
            create=True,
            require=True,
        )

        f_obj.data.require(
            data=data,
            axes_kwargs = [{"time_axis": {
                "data": nanostamps,
                "component_kwargs": {"axis": {"rate": sample_rate}},
            }}],
        )
        f_obj.data.components["timeseries"].time_axis.set_time_zone(tzinfo)

        if not open_:
            f_obj.close()

        self.xltek_data_group.insert_recursive_entry(
            paths=[day_name, file_name],
            start=start,
            end=Timestamp.fromnanostamp(nanostamps[-1]),
            length=len(nanostamps),
            min_shape=data.shape,
            max_shape=data.shape,
            sample_rate=sample_rate,
        )

        return f_obj
