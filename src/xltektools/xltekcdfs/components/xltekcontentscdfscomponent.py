""" xltekcontentscdfscomponent.py.py

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
from datetime import datetime
import pathlib
from typing import Any

# Third-Party Packages #
from cdfs.components import TimeContentsCDFSComponent
from dspobjects.time import Timestamp, nanostamp
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Local Packages #
from ...xltekhdf5 import XLTEKHDF5, XLTEKHDF5WriterTask
from ..arrays import XLTEKContentsProxy
from ..tables import BaseXLTEKContentsTable
from ..tasks import XLTEKContentsUpdateTask


# Definitions #
# Classes #
class XLTEKContentsCDFSComponent(TimeContentsCDFSComponent):
    # Attributes #
    date_format: str = "%d"
    time_format: str = "%H~%M~%S"

    _table: type[BaseXLTEKContentsTable] | None = None

    data_file_type: type[XLTEKHDF5] = XLTEKHDF5.get_latest_version_class()
    proxy_type: type[XLTEKContentsProxy] = XLTEKContentsProxy

    # Instance Methods #
    # Contents
    def correct_contents(
        self,
        path: pathlib.Path,
        session: Session | None = None,
        begin: bool = False,
    ) -> None:
        if session is not None:
            self.table.correct_contents(session=session, path=path, begin=begin)
        else:
            with self.create_session() as session:
                self.table.correct_contents(session=session, path=path, begin=True)

    async def correct_contents_async(
        self,
        path: pathlib.Path,
        session: AsyncSession | None = None,
        begin: bool = False,
    ) -> None:
        if session is not None:
            await self.table.correct_contents_async(session=session, path=path, begin=begin)
        else:
            async with self.create_async_session() as session:
                await self.table.correct_contents_async(session=session, path=path, begin=True)

    def get_start_end_ids(self, session: Session | None = None) -> tuple[tuple[int, int], ...]:
        if session is not None:
            return self.contents.get_start_end_ids(session=session)
        else:
            with self.create_session() as session:
                return self.contents.get_start_end_ids(session=session)

    async def get_start_end_ids_async(self, session: AsyncSession | None = None) -> tuple[tuple[int, int], ...]:
        if session is not None:
            return await self.contents.get_start_end_ids_async(session=session)
        else:
            async with self.create_async_session() as session:
                return await self.contents.get_start_end_ids_async(session=session)

    def insert_file_contents(
        self,
        path: pathlib.Path | str,
        file: XLTEKHDF5,
        update_id: int = 0,
        session: Session | None = None,
        begin: bool = False,
    ) -> None:
        if session is not None:
            self._table.insert(
                session=session,
                begin=begin,
                as_entry=True,
                update_id=update_id,
                path=path,
                shape=file.data.shape,
                axis=file.time_axis.axis,
                start=file.start_datetime,
                end=file.end_datetime,
                timezone=file.time_axis.tzinfo,
                sample_rate=file.sample_rate,
                start_id=file.attributes["start_id"],
                end_id=file.attributes["end_id"],
            )
        else:
            with self.create_session() as session:
                self._table.insert(
                    session=session,
                    begin=True,
                    as_entry=True,
                    update_id=update_id,
                    path=path,
                    shape=file.data.shape,
                    axis=file.time_axis.axis,
                    start=file.start_datetime,
                    end=file.end_datetime,
                    timezone=file.time_axis.tzinfo,
                    sample_rate=file.sample_rate,
                    start_id=file.attributes["start_id"],
                    end_id=file.attributes["end_id"],
                )

    async def insert_file_contents_async(
        self,
        path: pathlib.Path | str,
        file: XLTEKHDF5,
        update_id: int = 0,
        session: AsyncSession | None = None,
        begin: bool = False,
    ) -> None:
        if session is not None:
            await self._table.insert_async(
                session=session,
                begin=begin,
                as_entry=True,
                update_id=update_id,
                path=path,
                shape=file.data.shape,
                axis=file.time_axis.axis,
                start=file.start_datetime,
                end=file.end_datetime,
                timezone=file.time_axis.tzinfo,
                sample_rate=file.sample_rate,
                start_id=file.attributes["start_id"],
                end_id=file.attributes["end_id"],
            )
        else:
            async with self.create_async_session() as session:
                await self._table.insert_async(
                    session=session,
                    begin=begin,
                    as_entry=True,
                    update_id=update_id,
                    path=path,
                    shape=file.data.shape,
                    axis=file.time_axis.axis,
                    start=file.start_datetime,
                    end=file.end_datetime,
                    timezone=file.time_axis.tzinfo,
                    sample_rate=file.sample_rate,
                    start_id=file.attributes["start_id"],
                    end_id=file.attributes["end_id"],
                )

    def generate_day_name(self, start: datetime):
        absolute_start = self.start_datetime
        n_days = 1 if absolute_start is None else (start.date() - absolute_start.date()).days + 1
        return f"task-day{n_days:03d}"

    def generate_file_path(self, start, tzinfo=None):
        composite = self._composite()

        if not isinstance(start, datetime):
            start = Timestamp(start, tz=tzinfo)

        day_name = self.generate_day_name(start)
        day_path = composite.path / day_name
        day_path.mkdir(exist_ok=True)

        file_name = f"{composite.name}_{day_name}_acq-{start.strftime(f'{self.time_format}.%f')[:-3]}_ieeg.h5"

        return day_path / file_name, pathlib.Path(f"{day_name}/{file_name}")

    def generate_file_kwargs(self, start, tzinfo=None):
        file_path, _ = self.generate_file_path(start=start, tzinfo=tzinfo)
        return {"file": file_path, "name": self._composite().name}

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
            "file": {"file": full_path, "s_id": self._composite().name},
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
            name=self._composite().name,
            mode="a",
            create=True,
            construct=True,
        )
        f_obj.time_axis.components["axis"].set_time_zone(tzinfo)
        f_obj.time_axis.components["axis"].sample_rate = sample_rate
        f_obj.data.set_data(data, component_kwargs={"timeseries": {"data": nanostamps}})

        self.insert_file_contents(path=relative_path, file=f_obj, update_id=update_id, begin=True)

        if not open_:
            f_obj.close()

        return f_obj

    def create_data_writer(self, **kwargs) -> XLTEKHDF5WriterTask:
        return XLTEKHDF5WriterTask(file_type=self.data_file_type, **kwargs)

    def create_contents_updater(self, component_name, **kwargs) -> XLTEKContentsUpdateTask:
        return XLTEKContentsUpdateTask(cdfs=self.composite, component_name=component_name, **kwargs)
