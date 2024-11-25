""" xltekcontentstable.py

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
from pathlib import Path
from typing import Any

# Third-Party Packages #
from cdfs import BaseTimeContentsTableSchema, TimeContentsTableManifestation
from sqlalchemy import select, lambda_stmt
from sqlalchemy.orm import Session, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import BigInteger

# Local Packages #
from ...xltekhdf5 import XLTEKHDF5


# Definitions #
# Classes #
class BaseXLTEKContentsTableSchema(BaseTimeContentsTableSchema):
    __mapper_args__ = {"polymorphic_identity": "xltekcontents"}
    start_id = mapped_column(BigInteger, primary_key=True)
    end_id = mapped_column(BigInteger)

    file_type: type[XLTEKHDF5] | None = XLTEKHDF5

    # Class Methods #
    @classmethod
    def _correct_contents(cls, session: Session, path: Path) -> None:
        last_update_id = cls.get_last_update_id(session=session)
        update_id = 0 if last_update_id is None else last_update_id + 1

        # Correct registered entries
        registered = set()
        for item, in cls.get_all(session=session, as_entries=False):
            entry = item.as_entry()
            full_path = path / entry["path"]
            file = cls.file_type.new_validated(full_path)
            if file is not None:
                try:
                    file.standardize_attributes()
                except (KeyError, RuntimeError):
                    pass
                finally:
                    item.update({
                        "path": full_path.relative_to(path),
                        "shape": file.data.shape,
                        "axis": file.time_axis.components["axis"].axis,
                        "start": file.start_datetime,
                        "end": file.end_datetime,
                        "sample_rate": file.sample_rate,
                        "timezone": file.time_axis.components["axis"].tzinfo,
                        "start_id": int(file.start_id),
                        "end_id": int(file.end_id),
                        "update_id": update_id,
                    })
                    file.close()
            else:
                cls.delete_item(session=session, item=item)
            registered.add(full_path)

        # Correct unregistered
        entries = []
        for new_path in set(path.rglob("*.h5")) - registered:
            file = cls.file_type.new_validated(new_path)
            if file is not None:
                try:
                    file.standardize_attributes()
                except (KeyError, RuntimeError):
                    pass
                finally:
                    entries.append({
                        "path": new_path.relative_to(path),
                        "shape": file.data.shape,
                        "axis": file.time_axis.components["axis"].axis,
                        "start": file.start_datetime,
                        "end": file.end_datetime,
                        "sample_rate": file.sample_rate,
                        "timezone": file.time_axis.components["axis"].tzinfo,
                        "start_id": int(file.start_id),
                        "end_id": int(file.end_id),
                        "update_id": update_id,
                    })
                    file.close()
        if entries:
            cls.insert_all(session=session, items=entries, as_entries=True)

    @classmethod
    async def _correct_contents_async(cls, session: AsyncSession, path: Path) -> None:
        last_update_id = await cls.get_last_update_id_async(session=session)
        update_id = 0 if last_update_id is None else last_update_id + 1

        # Correct registered entries
        registered = set()
        for item, in await cls.get_all_async(session=session, as_entries=False):
            entry = item.as_entry()
            full_path = path / entry["path"]
            file = cls.file_type.new_validated(full_path)
            if file is not None:
                try:
                    file.standardize_attributes()
                except (KeyError, RuntimeError):
                    pass
                finally:
                    item.update({
                        "path": full_path.relative_to(path),
                        "shape": file.data.shape,
                        "axis": file.time_axis.components["axis"].axis,
                        "start": file.start_datetime,
                        "end": file.end_datetime,
                        "sample_rate": file.sample_rate,
                        "timezone": file.time_axis.components["axis"].tzinfo,
                        "start_id": int(file.start_id),
                        "end_id": int(file.end_id),
                        "update_id": update_id,
                    })
                    file.close()
            else:
                await cls.delete_item_async(session=session, item=item)
            registered.add(full_path)

        # Correct unregistered
        entries = []
        for new_path in set(path.rglob("*.h5")) - registered:
            file = cls.file_type.new_validated(new_path)
            if file is not None:
                try:
                    file.standardize_attributes()
                except (KeyError, RuntimeError):
                    pass
                finally:
                    entries.append({
                        "path": new_path.relative_to(path),
                        "shape": file.data.shape,
                        "axis": file.time_axis.components["axis"].axis,
                        "start": file.start_datetime,
                        "end": file.end_datetime,
                        "sample_rate": file.sample_rate,
                        "timezone": file.time_axis.components["axis"].tzinfo,
                        "start_id": int(file.start_id),
                        "end_id": int(file.end_id),
                        "update_id": update_id,
                    })
                    file.close()
        if entries:
            await cls.insert_all_async(session=session, items=entries, as_entries=True)

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


class XLTEKContentsTableManifestation(TimeContentsTableManifestation):
    # Instance Methods #
    # Contents
    def get_start_end_ids(self, session: Session | None = None) -> tuple[tuple[int, int], ...]:
        if session is not None:
            return self.table_schema.get_start_end_ids(session=session)
        else:
            with self.create_session() as session:
                return self.table_schema.get_start_end_ids(session=session)

    async def get_start_end_ids_async(self, session: AsyncSession | None = None) -> tuple[tuple[int, int], ...]:
        if session is not None:
            return await self.table_schema.get_start_end_ids_async(session=session)
        else:
            async with self.create_async_session() as session:
                return await self.table_schema.get_start_end_ids_async(session=session)
