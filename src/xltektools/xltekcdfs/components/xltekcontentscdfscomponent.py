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
import pathlib
from typing import Any
from weakref import ref

# Third-Party Packages #
from cdfs.components import TimeContentsCDFSComponent
from dspobjects.time import Timestamp
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Local Packages #
from ...xltekhdf5 import XLTEKHDF5
from ..arrays import XLTEKContentsProxy
from ..tables import BaseXLTEKContentsTable


# Definitions #
# Classes #
class XLTEKContentsCDFSComponent(TimeContentsCDFSComponent):
    # Attributes #
    _table: type[BaseXLTEKContentsTable] | None = None

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
        elif self.is_open:
            with self.create_session() as session:
                return self.contents.get_start_end_ids(session=session)
        else:
            raise IOError("File not open")

    async def get_start_end_ids_async(
        self,
        session: async_sessionmaker[AsyncSession] | AsyncSession | None = None,
    ) -> tuple[tuple[int, int], ...]:
        if session is not None:
            return await self.contents.get_start_end_ids_async(session=session)
        elif self.is_open:
            return await self.contents.get_start_end_ids_async(session=self.async_session_maker)
        else:
            raise IOError("File not open")

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
            await self._table.insert_async(
                session=self.async_session_maker,
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
