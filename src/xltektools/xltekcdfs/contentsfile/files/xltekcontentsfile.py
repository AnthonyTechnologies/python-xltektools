"""xltekcontentsfile.py

"""
# Package Header #
from ....header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import pathlib
from typing import Any

# Third-Party Packages #
from baseobjects import BaseObject
from cdfs.contentsfile import TimeContentsFile
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker

# Local Packages #
from ..bases import BaseXLTEKMetaInformationTable, BaseXLTEKContentsTable, BaseXLTEKVideosTable
from ....xltekhdf5 import XLTEKHDF5


# Definitions #
# Classes #
class XLTEKContentsFileAsyncSchema(AsyncAttrs, DeclarativeBase):
    pass


class XLTEKMetaInformationTable(BaseXLTEKMetaInformationTable, XLTEKContentsFileAsyncSchema):
    pass


class XLTEKContentsTable(BaseXLTEKContentsTable, XLTEKContentsFileAsyncSchema):
    pass


class XLTEKVideosTable(BaseXLTEKVideosTable, XLTEKContentsFileAsyncSchema):
    pass


class XLTEKContentsFile(TimeContentsFile):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    schema: type[DeclarativeBase] = XLTEKContentsFileAsyncSchema
    meta_information_table: type[XLTEKMetaInformationTable] = XLTEKMetaInformationTable
    contents: type[XLTEKContentsTable] = XLTEKContentsTable
    videos: type[XLTEKVideosTable] = XLTEKVideosTable

    # Magic Methods #
    # Construction/Destruction
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
            self.contents.insert(
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
        elif self.is_open:
            with self.create_session() as session:
                self.contents.insert(
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
        else:
            raise IOError("File not open")

    async def insert_file_contents_async(
        self,
        path: pathlib.Path | str,
        file: XLTEKHDF5,
        update_id: int = 0,
        session: async_sessionmaker[AsyncSession] | AsyncSession | None = None,
        begin: bool = False,
    ) -> None:
        if session is not None:
            await self.contents.insert_async(
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
        elif self.is_open:
            await self.contents.insert_async(
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
        else:
            raise IOError("File not open")
