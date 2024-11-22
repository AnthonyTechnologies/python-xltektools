""" xltekvideostable.py

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
from typing import Any

# Third-Party Packages #
from cdfs import BaseTimeContentsTable, TimeContentsTableManifestation
from sqlalchemy import select, lambda_stmt
from sqlalchemy.orm import Session, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import BigInteger

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKVideosTable(BaseTimeContentsTable):
    __tablename__ = "xltekvideos"
    __mapper_args__ = {"polymorphic_identity": "xltekvideos"}
    start_id = mapped_column(BigInteger)
    end_id = mapped_column(BigInteger)

    # Class Methods #
    @classmethod
    def get_start_end_ids(cls, session: Session) -> tuple[tuple[int, int], ...]:
        statement = lambda_stmt(lambda: select(cls.start_id, cls.end_id).order_by(cls.start_id))
        return tuple(session.execute(statement))

    @classmethod
    async def get_start_end_ids_async(cls, session: AsyncSession) -> tuple[tuple[int, int], ...]:
        statement = lambda_stmt(lambda: select(cls.start_id, cls.end_id).order_by(cls.start_id))
        return tuple(await session.execute(statement))

    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        dict_ = ({} if dict_ is None else dict_) | kwargs
        if (start_id := dict_.get("start_id", None)) is not None:
            self.start_id = start_id
        if (end_id := dict_.get("end_id", None)) is not None:
            self.end_id = end_id
        super().update(dict_)


class XLTEKVideosTableManifestation(TimeContentsTableManifestation):

    # Instance Methods #
    # Contents
    def get_start_end_ids(self, session: Session | None = None) -> tuple[tuple[int, int], ...]:
        if session is not None:
            return self.table.get_start_end_ids(session=session)
        else:
            with self.create_session() as session:
                return self.table.get_start_end_ids(session=session)

    async def get_start_end_ids_async(self, session: AsyncSession | None = None) -> tuple[tuple[int, int], ...]:
        if session is not None:
            return await self.table.get_start_end_ids_async(session=session)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_start_end_ids_async(session=session)