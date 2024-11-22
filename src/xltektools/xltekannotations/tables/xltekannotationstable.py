"""xltekannotationstable.py
A table containing the XLTEK annotation information common to all XLTEK annotations.
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
from datetime import datetime, timedelta
from datetime import tzinfo as TZInfo
from datetime import timezone as Timezone
import time
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

# Third-Party Packages #
from baseobjects.operations import timezone_offset
from dspobjects.time import Timestamp
from dspobjects.time import nanostamp as Nanostamp
import numpy as np
from sqlalchemy import select, func, lambda_stmt
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import BigInteger
from sqlalchemyobjects.tables import BaseUpdateTable, UpdateTableManifestation

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKAnnotationsTable(BaseUpdateTable):
    """A table containing the XLTEK annotation information common to all XLTEK annotations.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy.

    Columns:
        tz_offset: The timezone offset in seconds.
        nanostamp: The time of the annotation as a nanostamp. Defaults to None.
        title: The title of the annotation. Defaults to None.
        origin: The origin of the annotation. Defaults to None.
        comment: The comment of the annotation. Defaults to None.
        text: The text of the annotation. Defaults to None.
        type: The type of annotation. Defaults to None.
    """

    # Class Attributes #
    __tablename__ = "annotations"
    __mapper_args__ = {"polymorphic_identity": "annotations", "polymorphic_on": "type"}

    # Columns #
    tz_offset: Mapped[int]
    nanostamp = mapped_column(BigInteger)
    origin: Mapped[str]
    system_text: Mapped[str]
    text: Mapped[str]
    type: Mapped[str]

    # Class Methods #
    @classmethod
    def format_entry_kwargs(
        cls,
        id_: str | UUID | None = None,
        timezone: str | datetime | int | None = None,
        nanostamp: datetime | float | int | np.dtype | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Formats entry keyword arguments for creating or updating table entries.

        Args:
            id_: The ID of the entry, if specified.
            timezone: The timezone information. Defaults to None.
            nanostamp: The time of the annotation as a nanostamp. Defaults to None.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary of keyword arguments for the entry.
        """
        kwargs = super().format_entry_kwargs(id_=id_, **kwargs)

        if isinstance(timezone, str):
            if timezone.lower() == "local" or timezone.lower() == "localtime":
                timezone = time.localtime().tm_gmtoff
            else:
                timezone = ZoneInfo(timezone)  # Raises an error if the given string is not a time zone.

        tz_offset = timezone_offset(timezone).total_seconds() if isinstance(timezone, TZInfo) else timezone

        kwargs.update(
            tz_offset=tz_offset,
            timestamp=int(Nanostamp(nanostamp)),
        )
        return kwargs

    @classmethod
    def get_tz_offsets_distinct(cls, session: Session) -> tuple | None:
        """Gets distinct timezone offsets from the table.

        Args:
            session: The SQLAlchemy session to use for the query.

        Returns:
            tuple | None: A tuple of distinct timezone offsets, or None if no offsets are found.
        """
        offsets = session.execute(lambda_stmt(lambda: select(cls.tz_offset).distinct()))
        return None if offsets is None else tuple(offsets)

    @classmethod
    async def get_tz_offsets_distinct_async(cls, session: AsyncSession) -> tuple | None:
        """Asynchronously gets distinct timezone offsets from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.

        Returns:
            tuple | None: A tuple of distinct timezone offsets, or None if no offsets are found.
        """
        offsets = await session.execute(lambda_stmt(lambda: select(cls.tz_offset).distinct()))
        return None if offsets is None else tuple(offsets)

    @classmethod
    def get_start_datetime(cls, session: Session) -> Timestamp | None:
        """Gets the earliest start datetime from the table.

        Args:
            session: The SQLAlchemy session to use for the query.

        Returns:
            Timestamp | None: The earliest start datetime, or None if no start time is found.
        """
        offset, nanostamp_ = session.execute(lambda_stmt(lambda: select(cls.tz_offset, func.min(cls.nanostamp)))).first()
        if nanostamp_ is None:
            return None
        elif offset is None:
            return Timestamp.fromnanostamp(nanostamp_)
        else:
            return Timestamp.fromnanostamp(nanostamp_, Timezone(timedelta(seconds=offset)))

    @classmethod
    async def get_start_datetime_async(cls, session: AsyncSession) -> Timestamp | None:
        """Asynchronously gets the earliest start datetime from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.

        Returns:
            Timestamp | None: The earliest start datetime, or None if no start time is found.
        """
        results = await session.execute(lambda_stmt(lambda: select(cls.tz_offset, func.min(cls.nanostamp))))
        offset, nanostamp_ = results.first()
        if nanostamp_ is None:
            return None
        elif offset is None:
            return Timestamp.fromnanostamp(nanostamp_)
        else:
            return Timestamp.fromnanostamp(nanostamp_, Timezone(timedelta(seconds=offset)))

    @classmethod
    def get_end_datetime(cls, session: Session) -> Timestamp | None:
        """Gets the latest end datetime from the table.

        Args:
            session: The SQLAlchemy session to use for the query.

        Returns:
            Timestamp | None: The latest end datetime, or None if no end time is found.
        """
        offset, nanostamp_ = session.execute(lambda_stmt(lambda: select(cls.tz_offset, func.max(cls.nanostamp)))).first()
        if nanostamp_ is None:
            return None
        elif offset is None:
            return Timestamp.fromnanostamp(nanostamp_)
        else:
            return Timestamp.fromnanostamp(nanostamp_, Timezone(timedelta(seconds=offset)))

    @classmethod
    async def get_end_datetime_async(cls, session: AsyncSession) -> Timestamp | None:
        """Asynchronously gets the latest end datetime from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.

        Returns:
            Timestamp | None: The latest end datetime, or None if no end time is found.
        """
        results = await session.execute(lambda_stmt(lambda: select(cls.tz_offset, func.max(cls.nanostamp))))
        offset, nanostamp_ = results.first()
        if nanostamp_ is None:
            return None
        elif offset is None:
            return Timestamp.fromnanostamp(nanostamp_)
        else:
            return Timestamp.fromnanostamp(nanostamp_, Timezone(timedelta(seconds=offset)))

    @classmethod
    def get_all_nanostamps(cls, session: Session) -> tuple[tuple[int, int, int], ...]:
        """Gets all nanostamps from the table, ordered by start time.

        Args:
            session: The SQLAlchemy session to use for the query.

        Returns:
            tuple[tuple[int, int, int], ...]: A tuple of tuples containing start, end, and timezone offset.
        """
        statement = lambda_stmt(lambda: select(cls.nanostamp, cls.tz_offset).order_by(cls.nanostamp))
        return tuple(session.execute(statement))

    @classmethod
    async def get_all_nanostamps_async(cls, session: AsyncSession) -> tuple[tuple[int, int, int], ...]:
        """Asynchronously gets all nanostamps from the table, ordered by start time.

        Args:
            session: The SQLAlchemy async session to use for the query.

        Returns:
            tuple[tuple[int, int, int], ...]: A tuple of tuples containing start, end, and timezone offset.
        """
        statement = lambda_stmt(lambda: select(cls.nanostamp, cls.tz_offset).order_by(cls.nanostamp))
        return tuple(await session.execute(statement))

    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        """Updates the row of the table with the provided dictionary or keyword arguments.

        Args:
            dict_: A dictionary of attributes/columns to update. Defaults to None.
            **kwargs: Additional keyword arguments for the attributes to update.
        """
        dict_ = ({} if dict_ is None else dict_) | kwargs

        if (timezone := dict_.get("timezone", None)) is not None:
            if isinstance(timezone, str):
                if timezone.lower() == "local" or timezone.lower() == "localtime":
                    timezone = time.localtime().tm_gmtoff
                else:
                    timezone = ZoneInfo(timezone)  # Raises an error if the given string is not a time zone.

            if isinstance(timezone, TZInfo):
                self.tz_offset = int(timezone_offset(timezone).total_seconds())
            else:
                self.tz_offset = timezone

        if (nanostamp := dict_.get("naostampe", None)) is not None:
            self.nanostamp = int(Nanostamp(nanostamp))
        super().update(dict_)

    def as_dict(self) -> dict[str, Any]:
        """Creates a dictionary with all the contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the row.
        """
        entry = super().as_dict()
        entry.update(
            tz_offset=self.tz_offset,
            nanostamp=self.nanostamp,
        )
        return entry

    def as_entry(self) -> dict[str, Any]:
        """Creates a dictionary with the entry contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the entry.
        """
        entry = super().as_entry()
        tzone = Timezone(timedelta(seconds=self.tz_offset))
        entry.update(
            tz_offset=tzone,
            nanostamp=Timestamp.fromnanostamp(self.nanostamp, tzone),
        )
        return entry


class XLTEKAnnotationsTableManifestation(UpdateTableManifestation):
    """The manifestation of a XLTEKAnnotationsTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table: The SQLAlchemy declarative table which this object act as the interface for.

    Args:
        table: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """

    # Properties #
    @property
    def start_datetime(self):
        """Gets the start datetime.

        Returns:
            Timestamp: The start datetime.
        """
        return self.get_start_datetime()

    @property
    def end_datetime(self):
        """Gets the end datetime.

        Returns:
            Timestamp: The end datetime.
        """
        return self.get_end_datetime()

    # Instance Methods #
    # Meta Information
    def get_tz_offsets_distinct(self, session: Session | None = None) -> Timestamp:
        """Gets distinct timezone offsets from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            Timestamp: The distinct timezone offsets.
        """
        if session is not None:
            return self.table.get_tz_offsets_distinct(session=session)
        else:
            with self.create_session() as session:
                return self.table.get_tz_offsets_distinct(session=session)

    async def get_tz_offsets_distinct_async(self, session: Session | None = None) -> Timestamp:
        """Asynchronously gets distinct timezone offsets from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            Timestamp: The distinct timezone offsets.
        """
        if session is not None:
            return await self.table.get_tz_offsets_distinct_async(session=session)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_tz_offsets_distinct_async(session=session)

    def get_start_datetime(self, session: Session | None = None) -> Timestamp:
        """Gets the start datetime from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            Timestamp: The start datetime.
        """
        if session is not None:
            return self.table.get_start_datetime(session=session)
        else:
            with self.create_session() as session:
                return self.table.get_start_datetime(session=session)

    async def get_start_datetime_async(self, session: AsyncSession | None = None) -> Timestamp:
        """Asynchronously gets the start datetime from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            Timestamp: The start datetime.
        """
        if session is not None:
            return await self.table.get_start_datetime_async(session=session)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_start_datetime_async(session=session)

    def get_end_datetime(self, session: Session | None = None) -> Timestamp:
        """Gets the end datetime from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            Timestamp: The end datetime.
        """
        if session is not None:
            return self.table.get_end_datetime(session=session)
        else:
            with self.create_session() as session:
                return self.table.get_end_datetime(session=session)

    async def get_end_datetime_async(self, session: AsyncSession | None = None) -> Timestamp:
        """Asynchronously gets the end datetime from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            Timestamp: The end datetime.
        """
        if session is not None:
            return await self.table.get_end_datetime_async(session=session)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_end_datetime_async(session=session)

    def get_contents_nanostamps(self, session: Session | None = None) -> tuple[tuple[int, int, int], ...]:
        """Gets all nanostamps from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            tuple[tuple[int, int, int], ...]: The nanostamps.
        """
        if session is not None:
            return self.table.get_all_nanostamps(session=session)
        else:
            with self.create_session() as session:
                return self.table.get_all_nanostamps(session=session)

    async def get_contents_nanostamps_async(
        self,
        session: AsyncSession | None = None,
    ) -> tuple[tuple[int, int, int], ...]:
        """Asynchronously gets all nanostamps from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            tuple[tuple[int, int, int], ...]: The nanostamps.
        """
        if session is not None:
            return await self.table.get_all_nanostamps_async(session=session)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_all_nanostamps_async(session=session)
