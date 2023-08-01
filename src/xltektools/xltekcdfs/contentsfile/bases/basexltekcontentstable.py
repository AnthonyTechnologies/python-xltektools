""" basexltekcontentstable.py
A node component which implements time content information in its dataset.
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
from baseobjects import singlekwargdispatch
from cdfs.contentsfile import BaseTimeContentsTable
from sqlalchemy import select, func, lambda_stmt
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.types import BigInteger

# Local Packages #
from ....xltekhdf5 import XLTEKHDF5


# Definitions #
# Classes #
class BaseXLTEKContentsTable(BaseTimeContentsTable):
    __mapper_args__ = {"polymorphic_identity": "xltekcontents"}
    start_id = mapped_column(BigInteger)
    end_id = mapped_column(BigInteger)

    file_type: type[XLTEKHDF5] | None = XLTEKHDF5

    # Class Methods #
    @classmethod
    def _correct_contents(cls, session: Session, path: pathlib.Path) -> None:
        # Correct registered entries
        registered = set()
        for item in cls.get_all(session=session, as_entries=False):
            entry = item.as_entry()
            full_path = path / entry["path"]
            with cls.file_type.new_validated(full_path) as file:
                if file is not None:
                    item.update({
                        "path": file.path.name,
                        "start": file.start_datetime,
                        "end": file.end_datetime,
                        "sample_rate": file.sample_rate,
                        "shape": file.data.shape,
                        "start_id": file.start_id,
                        "end_id": file.end_id,
                    })
                    file.close()
            registered.add(full_path)

        # Correct unregistered
        entries = []
        for new_path in set(path.rglob("*.h5")) - registered:
            file = cls.file_type.new_validated(new_path)
            if file is not None:
                entries.append({
                    "path": file.path.name,
                    "start": file.start_datetime,
                    "end": file.end_datetime,
                    "sample_rate": file.sample_rate,
                    "shape": file.data.shape,
                    "start_id": file.start_id,
                    "end_id": file.end_id,
                })
                file.close()
        cls.insert_all(session=session, items=entries, as_entries=True)

    @classmethod
    def correct_contents(cls, session: Session, path: pathlib.Path, begin: bool = False) -> None:
        if begin:
            with session.begin():
                cls._correct_contents(session=session, path=path)
        else:
            cls._correct_contents(session=session, path=path)

    @classmethod
    async def _correct_contents_async(cls, session: AsyncSession, path: pathlib.Path) -> None:
        # Correct registered entries
        registered = set()
        for item in await cls.get_all_async(session=session, as_entries=False):
            entry = item.as_entry()
            full_path = path / entry["path"]
            with cls.file_type.new_validated(full_path) as file:
                if file is not None:
                    item.update({
                        "path": file.path.name,
                        "start": file.start_datetime,
                        "end": file.end_datetime,
                        "sample_rate": file.sample_rate,
                        "shape": file.data.shape,
                        "start_id": file.start_id,
                        "end_id": file.end_id,
                    })
                    file.close()
            registered.add(full_path)

        # Correct unregistered
        entries = []
        for new_path in set(path.rglob("*.h5")) - registered:
            file = cls.file_type.new_validated(new_path)
            if file is not None:
                entries.append({
                    "path": file.path.name,
                    "start": file.start_datetime,
                    "end": file.end_datetime,
                    "sample_rate": file.sample_rate,
                    "shape": file.data.shape,
                    "start_id": file.start_id,
                    "end_id": file.end_id,
                })
                file.close()
        await cls.insert_all_async(session=session, items=entries, as_entries=True)

    @singlekwargdispatch(kwarg="session")
    @classmethod
    async def correct_contents_async(
        cls,
        session: async_sessionmaker[AsyncSession] | AsyncSession,
        path: pathlib.Path,
        begin: bool = False,
    ) -> None:
        raise TypeError(f"{type(session)} is not a valid type.")

    @correct_contents_async.register(async_sessionmaker)
    @classmethod
    async def __correct_contents_async(
        cls,
        session: async_sessionmaker[AsyncSession],
        path: pathlib.Path,
        begin: bool = False,
    ) -> None:
        async with session() as async_session:
            async with async_session.begin():
                await cls._correct_contents_async(session=async_session, path=path)

    @correct_contents_async.register(AsyncSession)
    @classmethod
    async def __correct_contents_async(cls, session: AsyncSession, path: pathlib.Path, begin: bool = False,) -> None:
        if begin:
            async with session.begin():
                await cls._correct_contents_async(session=session, path=path)
        else:
            await cls._correct_contents_async(session=session, path=path)

    @classmethod
    def get_start_end_ids(cls, session: Session) -> tuple[tuple[int, int], ...]:
        statement = lambda_stmt(lambda: select(cls.start_id, cls.end_id).order_by(cls.start_id))
        return tuple(session.execute(statement))

    @singlekwargdispatch(kwarg="session")
    @classmethod
    async def get_start_end_ids_async(
        cls,
        session: async_sessionmaker[AsyncSession] | AsyncSession,
    ) -> tuple[tuple[int, int], ...]:
        raise TypeError(f"{type(session)} is not a valid type.")

    @get_start_end_ids_async.register(async_sessionmaker)
    @classmethod
    async def _get_start_end_ids_async(
        cls,
        session: async_sessionmaker[AsyncSession],
    ) -> tuple[tuple[int, int], ...]:
        statement = lambda_stmt(lambda: select(cls.start_id, cls.end_id).order_by(cls.start_id))
        async with session() as async_session:
            return tuple(await async_session.execute(statement))

    @get_start_end_ids_async.register(AsyncSession)
    @classmethod
    async def _get_start_end_ids_async(cls, session: AsyncSession) -> tuple[tuple[int, int], ...]:
        statement = lambda_stmt(lambda: select(cls.start_id, cls.end_id).order_by(cls.start_id))
        return tuple(await session.execute(statement))
    
    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        dict_ = ({} if dict_ is None else dict_) | kwargs
        if start_id := dict_.get("start_id", None) is not None:
            self.start_id = start_id
        if end_id := dict_.get("end_id", None) is not None:
            self.end_id = end_id
        super().update(dict_)
