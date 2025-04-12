""" xltekmetainformationtable.py

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
import datetime
from datetime import timedelta, timezone as Timezone
from typing import Any
import time
from zoneinfo import ZoneInfo

# Third-Party Packages #
from baseobjects.operations import timezone_offset
from dspobjects.time import Timestamp, nanostamp
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger
from sqlalchemyobjects.tables import BaseUpdateTableSchema, UpdateTableManifestation
from sqlalchemyobjects.tables import BaseMetaInformationTableSchema, MetaInformationTableManifestation

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKMetaInformationTableSchema(BaseMetaInformationTableSchema, BaseUpdateTableSchema):
    __mapper_args__ = {"polymorphic_identity": "xltekmetainfromation"}

    name: Mapped[str] = mapped_column(nullable=True)
    start = mapped_column(BigInteger, nullable=True)
    tz_offset: Mapped[int] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    sex: Mapped[str] = mapped_column(default="U", nullable=True)
    species: Mapped[str] = mapped_column(default="Homo Sapien", nullable=True)
    recording_unit: Mapped[str] = mapped_column(default="microvolts", nullable=True)

    # Class Methods #
    # Base
    @classmethod
    def to_sql_types(cls, dict_: dict[str, Any] | None = None, /, **kwargs) -> dict[str, Any]:
        """Casts Python types of an entry to SQLAlchemy types.

        Only table item elements (columns) which must cast to an SQLAlchemy type are cast to SQLAlchemy types.
        Additionally, all elements are optional, such that they do not need to be provided. This way any subset of the
        elements can cast. For example: when updating a table item, a few elements can updated without providing all
        elements.

        Args:
            dict_: A dictionary representing the entry with Python types.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary representing the entry with SQLAlchemy types.
        """
        # Format parent entry
        sql_entry = super().to_sql_types(dict_, **kwargs)

        # Format
        if (tz_offset := sql_entry.get("tz_offset", None)) is not None:
            match tz_offset:
                case int():
                    pass
                case ZoneInfo():
                    sql_entry["tz_offset"] = int(timezone_offset(tz_offset).total_seconds())
                case str():
                    if tz_offset.lower() in {"local", "localtime"}:
                        sql_entry["tz_offset"] = time.localtime().tm_gmtoff
                    else:
                        sql_entry["tz_offset"] = int(timezone_offset(ZoneInfo(tz_offset)).total_seconds())

        if (start := sql_entry.get("start", None)) is not None:
            match start:
                case int():
                    pass
                case _:
                    sql_entry["start"] = int(nanostamp(start))

        # Return formatted entry
        return sql_entry

    @classmethod
    def from_sql_types(cls, dict_: dict[str, Any] | None = None, /, **kwargs: Any) -> dict[str, Any]:
        """Casts SQLAlchemy types of an entry to Python types.

        Only table item elements (columns) which must cast to a Python type are cast to Python types. Additionally, all
        elements are optional, such that they do not need to be provided. This way any subset of the elements can cast.
        For example: when querying a table item, a few columns can be selected without providing all columns.

        Args:
            dict_: A dictionary representing the entry with SQLAlchemy types.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary representing the entry with Python types.
        """
        # Format parent entry
        python_entry = super().from_sql_types(dict_, **kwargs)

        # Format
        t_zone = None
        if (tz_offset := python_entry.get("tz_offset", None)) is not None:
            python_entry["tz_offset"] = t_zone = Timezone(timedelta(seconds=tz_offset))

        if (start := python_entry.get("start", None)) is not None:
            python_entry["start"] = Timestamp.fromnanostamp(start, t_zone)

        # Return formatted entry
        return python_entry


class XLTEKMetaInformationTableManifestation(MetaInformationTableManifestation, UpdateTableManifestation):
    # Properties #
    @property
    def name(self) -> str | None:
        """The subject ID from the file attributes."""
        return self.meta_information["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.set_meta_information(name=value)

    @property
    def start_datetime(self):
        return self.meta_information["start"]

    @start_datetime.setter
    def start_datetime(self, value: datetime.datetime) -> None:
        self.set_meta_information(start=value, timezone=value.tzinfo)
    
    @property
    def timezone(self):
        return self.meta_information["timezone"]
    
    @timezone.setter
    def timezone(self, value: datetime.tzinfo | str) -> None:
        self.set_meta_information(timezone=value)
        
    @property
    def age(self):
        return self.meta_information["age"]
    
    @age.setter
    def age(self, value: int) -> None:
        self.set_meta_information(age=value)

    @property
    def sex(self):
        return self.meta_information["sex"]

    @sex.setter
    def sex(self, value: int) -> None:
        self.set_meta_information(sex=value)

    @property
    def species(self):
        return self.meta_information["species"]

    @species.setter
    def species(self, value: str) -> None:
        self.set_meta_information(species=value)

    @property
    def recording_unit(self):
        return self.meta_information["recording_unit"]

    @recording_unit.setter
    def recording_unit(self, value: str) -> None:
        self.set_meta_information(recording_unit=value)
        