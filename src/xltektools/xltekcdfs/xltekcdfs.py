"""xltekcdfs.py

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
from datetime import datetime
from datetime import timedelta
import pathlib
from typing import Any

# Third-Party Packages #
from baseobjects.cachingtools import timed_keyless_cache
from cdfs import CDFS
from dspobjects.time import Timestamp, nanostamp
import numpy as np
from sqlalchemy import select, func, lambda_stmt
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Local Packages #
from ..xltekhdf5 import XLTEKHDF5, XLTEKHDF5WriterTask
from .contentsfile import XLTEKContentsFile, XLTEKContentsUpdateTask
from .arrays import XLTEKContentsProxy


# Definitions #
# Classes #
class XLTEKCDFS(CDFS):
    """

    Class Attributes:

    Attributes:

    Args:

    """

    default_component_types: dict[str, tuple[type, dict[str, Any]]] = {}
    default_proxy_type: type = XLTEKContentsProxy
    default_data_file_type: type[XLTEKHDF5] = XLTEKHDF5.get_latest_version_class()
    contents_file_type: type = XLTEKContentsFile

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: pathlib.Path | str | None = None,
        name: str | None = None,
        s_dir: pathlib.Path | None = None,
        mode: str = "r",
        open_: bool = False,
        load: bool = False,
        create: bool = False,
        update: bool = False,
        contents_name: str | None = None,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self._subjects_dir: pathlib.Path | None = None

        self._name: str | None = None

        self.date_format: str = "%d"
        self.time_format: str = "%H~%M~%S"

        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(
                path=path,
                name=name,
                s_dir=s_dir,
                mode=mode,
                open_=open_,
                load=load,
                create=create,
                update=update,
                contents_name=contents_name,
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
    def name(self) -> str | None:
        """The subject ID from the file attributes."""
        return self.contents_file.meta_information["name"]

    @name.setter
    def name(self, value: str) -> None:
        if self.contents_file is not None and self.contents_file.is_open:
            self.contents_file.set_meta_information(name=value)
        self._name = value

    @property
    def start_datetime(self):
        if self._start_datetime is None or self.get_start_datetime.clear_condition():
            return self.get_start_datetime()
        return self._start_datetime

    @start_datetime.setter
    def start_datetime(self, value: Timestamp) -> None:
        if self.contents_file is not None and self.contents_file.is_open:
            self.contents_file.set_meta_information(start=value, timezone=value.tzinfo)
        self._start_datetime = value

    # Instance Methods
    # Constructors/Destructors
    def construct(
        self,
        path: pathlib.Path | str | None = None,
        name: str | None = None,
        s_dir: pathlib.Path | None = None,
        mode: str = "r",
        open_: bool = False,
        load: bool = False,
        create: bool = False,
        update: bool = False,
        contents_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            path: The path for this proxy to wrap.
            name: The subject ID.
            studies_path: The parent directory to this XLTEK study proxy.
            mode: Determines if the contents of this proxy are editable or not.
            update: Determines if this proxy will start_timestamp updating or not.
            open_: Determines if the arrays will remain open after construction.
            load: Determines if the arrays will be constructed.
            **kwargs: The keyword arguments to create contained arrays.
        """
        if name is not None:
            self._name = name

        if s_dir is not None:
            self.subjects_dir = s_dir

        if path is None and self.path is None and self.name is not None and self.subjects_dir is not None:
            self.path = self.subjects_dir / self.name

        super().construct(
            path=path,
            mode=mode,
            open_=open_,
            load=load,
            create=create,
            update=update,
            contents_name=contents_name,
            **kwargs,
        )

    # Contents File
    def open_contents_file(
        self,
        create: bool = False,
        **kwargs: Any,
    ) -> None:
        if not self.contents_path.is_file() and not create:
            raise ValueError("Contents file does not exist.")
        elif self.contents_file is None:
            self.contents_file = self.contents_file_type(
                path=self.contents_path,
                open_=True,
                create=create,
                **kwargs,
            )
            if create and self._mode in {"a", "w"}:
                self.save_cached_meta_information()
        else:
            self.contents_file.open(**kwargs)

    def save_cached_meta_information(self):
        info = self.contents_file.get_meta_information()
        new_info = {}
        if info["name"] is None:
            new_info["name"] = self._name
        if self._start_datetime is not None:
            if info["start"] is None:
                new_info["start"] = self._start_datetime
            if info["tz_offset"] is None:
                new_info["timezone"] = self._start_datetime.tzinfo
        if new_info:
            self.contents_file.set_meta_information(entry=new_info)

    @timed_keyless_cache(call_method="clearing_call", local=True)
    def get_start_datetime(self, session: Session | None = None) -> Timestamp | None:
        self._start_datetime = self.contents_file.get_meta_information(session=session)["start"]
        return self._start_datetime

    async def get_start_datetime_async(
        self,
        session: async_sessionmaker[AsyncSession] | AsyncSession | None = None,
    ) -> Timestamp:
        self._start_datetime = (await self.contents_file.get_meta_information_async(session=session))["start"]
        self.get_start_datetime.refresh_expiration()
        return self._start_datetime

    # Contents
    def get_start_end_ids(self, session: Session | None = None) -> tuple[tuple[int, int], ...]:
        return self.contents_file.get_start_end_ids(session=session)

    async def get_start_end_ids_async(
        self,
        session: async_sessionmaker[AsyncSession] | AsyncSession | None = None,
    ) -> tuple[tuple[int, int], ...]:
        return await self.contents_file.get_start_end_ids_async(session=session)

    def generate_day_name(self, start: datetime):
        absolute_start = self.start_datetime
        n_days = 1 if absolute_start is None else (start.date() - absolute_start.date()).days + 1
        return f"task-day{n_days:03d}"

    def generate_file_path(self, start, tzinfo=None):
        if not isinstance(start, datetime):
            start = Timestamp(start, tz=tzinfo)

        day_name = self.generate_day_name(start)
        day_path = self.path / day_name
        day_path.mkdir(exist_ok=True)

        file_name = f"{self.name}_{day_name}_acq-{start.strftime(f'{self.time_format}.%f')[:-3]}_ieeg.h5"

        return day_path / file_name, pathlib.Path(f"{day_name}/{file_name}")

    def generate_file_kwargs(self, start, tzinfo=None):
        file_path, _ = self.generate_file_path(start=start, tzinfo=tzinfo)
        return {"file": file_path, "name": self.name}

    def generate_file_entry_kwargs(
        self,
        shape: tuple[int, ...],
        sample_rate: int,
        start: datetime | float | int | np.dtype | np.ndarray, 
        end: datetime | float | int | np.dtype | np.ndarray | None = None,
        tzinfo=None,
        start_id: int | None = None,
        end_id: int | None = None,
        axis: int = 0,
        update_id: int = 0,
    ) -> dict:
        if not isinstance(start, Timestamp):
            start = Timestamp(start, tz=tzinfo)
            
        if end is None:
            end = start
        elif not isinstance(end, Timestamp):
            end = Timestamp(end, tz=tzinfo)

        full_path, relative_path = self.generate_file_path(start=start, tzinfo=tzinfo)

        return {
            "file": {"file": full_path, "s_id": self.name},
            "contents_insert": {
                "update_id": update_id,
                "path": relative_path,
                "shape": shape,
                "axis": axis,
                "timezone": tzinfo,
                "start": start,
                "end": end,
                "sample_rate": sample_rate,
                "start_id": int(nanostamp(start)) if start_id is None else start_id,
                "end_id": int(nanostamp(end)) if end_id is None else end_id,
            },
        }

    def create_data_file(self, data, nanostamps, sample_rate, tzinfo=None, update_id: int = 0, open_: bool = False):
        start = Timestamp(nanostamps[0], tz=tzinfo)

        full_path, relative_path = self.generate_file_path(start=start, tzinfo=tzinfo)
        f_obj = self.data_file_type(
            file=full_path,
            name=self.name,
            mode="a",
            create=True,
            construct=True,
        )
        f_obj.time_axis.components["axis"].set_time_zone(tzinfo)
        f_obj.time_axis.components["axis"].sample_rate = sample_rate
        f_obj.data.set_data(data, component_kwargs={"timeseries": {"data": nanostamps}})

        self.contents_file.insert_file_contents(path=relative_path, file=f_obj, update_id=update_id, begin=True)

        if not open_:
            f_obj.close()

        return f_obj

    def create_data_writer(self, **kwargs) -> XLTEKHDF5WriterTask:
        return XLTEKHDF5WriterTask(file_type=self.data_file_type, **kwargs)

    def create_contents_updater(self, **kwargs) -> XLTEKContentsUpdateTask:
        return XLTEKContentsUpdateTask(contents_file=self.contents_file, **kwargs)

    # Video
    def insert_video_entry_start(self, name, start, end, proxies=0, sample_rate=np.nan, tzinfo=None):
        raise NotImplementedError
