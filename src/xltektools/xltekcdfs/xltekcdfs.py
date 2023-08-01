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
from cdfs import CDFS
from dspobjects.time import Timestamp, nanostamp
import numpy as np
from sqlalchemy import select, func, lambda_stmt
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Local Packages #
from ..xltekhdf5 import XLTEKHDF5, XLTEKHDF5KWriterTask
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
        s_id: str | None = None,
        s_dir: pathlib.Path | None = None,
        mode: str = "r",
        update: bool = False,
        open_: bool = False,
        load: bool = False,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self._subjects_dir: pathlib.Path | None = None

        self._subject_id: str | None = None

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
        return self.contents_file.meta_information["subject_id"]

    @subject_id.setter
    def subject_id(self, value: str) -> None:
        if self.contents_file is not None and not self.contents_file.is_open:
            self.contents_file.set_meta_information(subject_id=self.subject_id)
        self._subject_id = value

    def __del__(self) -> None:
        if self.writer_process is not None and self.writer_process.is_alive():
            self.stop_data_writer_process()

    # Instance Methods
    # Constructors/Destructors
    def construct(
        self,
        path: pathlib.Path | str | None = None,
        s_id: str | None = None,
        s_dir: pathlib.Path | None = None,
        mode: str = "r",
        update: bool = False,
        open_: bool = False,
        load: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            path: The path for this proxy to wrap.
            s_id: The subject ID.
            studies_path: The parent directory to this XLTEK study proxy.
            proxies: An iterable holding arrays/objects to store in this proxy.
            mode: Determines if the contents of this proxy are editable or not.
            update: Determines if this proxy will start_timestamp updating or not.
            open_: Determines if the arrays will remain open after construction.
            load: Determines if the arrays will be constructed.
            **kwargs: The keyword arguments to create contained arrays.
        """
        if s_id is not None:
            self._subject_id = s_id

        if s_dir is not None:
            self.subjects_dir = s_dir

        if path is None and self.path is None and self.subject_id is not None and self.subjects_dir is not None:
            self.path = self.subjects_dir / self.subject_id

        super().construct(path=path, mode=mode, update=update, open_=open_, load=load, **kwargs)

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
        return f"{self.subject_id}_Day-{n_days}"

    def generate_file_path(self, start, tzinfo=None):
        if not isinstance(start, Timestamp):
            start = Timestamp(start, tz=tzinfo)

        day_name = self.generate_day_name(start)
        day_path = self.path / day_name
        day_path.mkdir(exist_ok=True)

        file_name = f"{day_name}_{start.strftime(f'{self.time_format}.%f')[:-3]}.h5"

        return day_path / file_name, pathlib.Path(f"{day_name}/{file_name}")

    def generate_file_kwargs(self, start, tzinfo=None):
        file_path, _ = self.generate_file_path(start=start, tzinfo=tzinfo)
        return {"file": file_path, "s_id": self.subject_id}

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
            "file": {"file": full_path, "s_id": self.subject_id},
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
            s_id=self.subject_id,
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

    def create_data_writer(self, **kwargs) -> XLTEKHDF5KWriterTask:
        return XLTEKHDF5KWriterTask(file_type=self.data_file_type, **kwargs)

    def create_contents_updater(self, **kwargs) -> XLTEKContentsUpdateTask:
        return XLTEKContentsUpdateTask(contents_file=self.contents_file, **kwargs)

    # Video
    def insert_video_entry_start(self, name, start, end, proxies=0, sample_rate=np.nan, tzinfo=None):
        raise NotImplementedError
