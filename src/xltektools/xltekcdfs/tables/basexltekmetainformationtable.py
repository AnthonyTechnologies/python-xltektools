""" basexltekmetainformationtable.py
A node component which implements time content information in its dataset.
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
from typing import Any
import time
import zoneinfo

# Third-Party Packages #
from baseobjects.operations import timezone_offset
from cdfs.tables import BaseMetaInformationTable
from dspobjects.time import Timestamp, nanostamp
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKMetaInformationTable(BaseMetaInformationTable):
    __mapper_args__ = {"polymorphic_identity": "xltekmetainfromation"}
    name: Mapped[str] = mapped_column(nullable=True)
    start = mapped_column(BigInteger, nullable=True)
    tz_offset: Mapped[int] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    sex: Mapped[str] = mapped_column(default="U", nullable=True)
    species: Mapped[str] = mapped_column(default="Homo Sapien", nullable=True)
    recording_unit: Mapped[str] = mapped_column(default="microvolts", nullable=True)

    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        dict_ = ({} if dict_ is None else dict_) | kwargs

        if (timezone := dict_.get("timezone", None)) is not None:
            if isinstance(timezone, str):
                if timezone.lower() == "local" or timezone.lower() == "localtime":
                    timezone = time.localtime().tm_gmtoff
                else:
                    timezone = zoneinfo.ZoneInfo(timezone)  # Raises an error if the given string is not a time zone.

            if isinstance(timezone, datetime.tzinfo):
                self.tz_offset = timezone_offset(timezone).total_seconds()
            else:
                self.tz_offset = timezone

        if (start := dict_.get("start", None)) is not None:
            self.start = int(nanostamp(start))

        if (name := dict_.get("name", None)) is not None:
            self.name = name
        if (age := dict_.get("age", None)) is not None:
            self.age = age
        if (sex := dict_.get("sex", None)) is not None:
            self.sex = sex
        if (sepcies := dict_.get("sepcies", None)) is not None:
            self.sepcies = sepcies
        if (recording_unit := dict_.get("recording_unit", None)) is not None:
            self.recording_unit = recording_unit

        super().update(dict_)

    def as_dict(self) -> dict[str, Any]:
        entry = super().as_dict()
        entry.update(
            name=self.name,
            start=self.start,
            tz_offset=self.tz_offset,
            age=self.age,
            sex=self.sex,
            species=self.species,
            recording_unit=self.recording_unit,
        )
        return entry

    def as_entry(self) -> dict[str, Any]:
        entry = super().as_entry()
        tzone = None if self.tz_offset is None else datetime.timezone(datetime.timedelta(seconds=self.tz_offset))
        if self.start is None:
            start = None
        elif tzone is None:
            start = Timestamp.fromnanostamp(self.start)
        else:
            start = Timestamp.fromnanostamp(self.start, tzone)
        entry.update(
            name=self.name,
            tz_offset=tzone,
            start=start,
            age=self.age,
            sex=self.sex,
            species=self.species,
            recording_unit=self.recording_unit,
        )
        return entry
