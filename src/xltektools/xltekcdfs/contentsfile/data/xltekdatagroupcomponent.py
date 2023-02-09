""" xltekdatagroupcomponent.py

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
from datetime import datetime, date, tzinfo
from decimal import Decimal
from typing import Any
import uuid

# Third-Party Packages #
from dspobjects.time import Timestamp
from hdf5objects import HDF5Map, HDF5Dataset
from hdf5objects import HDF5BaseComponent
import numpy as np

# Local Packages #


# Definitions #
# Classes #
class XLTEKDataGroupComponent(HDF5BaseComponent):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        composite: Any = None,
        day_map_type: type | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.day_map_type: type | None = None
        self.days_dataset_name = "days"
        self._days_dataset = None

        # Parent Attributes #
        super().__init__(self, init=False)

        # Object Construction #
        if init:
            self.construct(
                composite=composite,
                day_map_type=day_map_type,
                **kwargs,
            )

    @property
    def days_dataset(self) -> HDF5Dataset | None:
        """Loads and returns the id axis."""
        if self._days_dataset is None:
            self._days_dataset = self.composite[self.days_dataset_name]
        return self._days_dataset

    @days_dataset.setter
    def days_dataset(self, value: HDF5Dataset | None) -> None:
        self._days_dataset = value

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        composite: Any = None,
        day_map_type: type | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            composite: The object which this object is a component of.
            **kwargs: Keyword arguments for inheritance.
        """
        if day_map_type is not None:
            self.day_map_type = day_map_type

        super().construct(composite=composite, **kwargs)

    def get_start_datetime(self):
        if self.days_dataset.size == 0:
            return None
        else:
            return self.days_dataset.components["start_times"].start_datetime

    def get_end_datetime(self):
        if self.days_dataset.size == 0:
            return None
        else:
            return self.days_dataset.components["end_times"].end_datetime

    def set_time_zone(self, value: str | tzinfo | None = None, offset: float | None = None) -> None:
        """Sets the timezone of the start and end time axes.

        Args:
            value: The time zone to set this axis to.
            offset: The time zone offset from UTC.
        """
        self.days_dataset.components["start_times"].set_tzinfo(value)
        self.days_dataset.components["end_times"].set_tzinfo(value)
        if self.days_dataset.size != 0:
            for day in self.days_dataset.components["object_reference"].get_objects_iter():
                day.components["start_times"].set_tzinfo(value)
                day.components["end_times"].set_tzinfo(value)

    def find_day_start(self, start, approx=True, tails=True, sentinel: Any = (None, None)):
        start = Timestamp(start.date(), tz=start.tzinfo)

        if self.days_dataset.size != 0:
            return self.days_dataset.components["start_times"].find_time_index(start, approx=approx, tails=tails)
        else:
            return sentinel

    def create_day(
        self,
        start: datetime | date | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        path: str | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        min_shape: tuple[int] = (),
        max_shape: tuple[int] = (),
        sample_rate: float | str | Decimal | None = None,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        if isinstance(start, date):
            start = Timestamp(start)

        if path is None:
            path = start.date().strftime(self.date_format)

        if map_ is None:
            map_ = self.day_map_type(name=f"{self.composite.name}/{path}")
            self.composite.map.set_item(map_)

        self.days_dataset.components["node_content"].insert_entry_start(
            path=path,
            length=length,
            map_=map_,
            start=start,
            end=end,
            min_shape=min_shape,
            max_shape=max_shape,
            sample_rate=sample_rate,
            id_=id_,
        )

        start_tz = self.days_dataset.components["start_times"].time_axis.time_zone
        end_tz = self.days_dataset.components["end_times"].time_axis.time_zone

        day = self.composite[map_.name]
        if start_tz is not None:
            day.components["start_times"].set_tzinfo(start_tz)

        if end_tz is not None:
            day.components["end_times"].set_tzinfo(end_tz)

        return day

    def require_day(
        self,
        start: datetime | date | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        path: str | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        min_shape: tuple[int] = (),
        max_shape: tuple[int] = (),
        sample_rate: float | str | Decimal | None = None,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        if isinstance(start, date):
            start = Timestamp(start)

        if self.days_dataset.size != 0:
            index, dt = self.days_dataset.components["start_times"].find_time_index(start, approx=True, tails=True)

            if dt.date() == start.date():
                return self.days_dataset.components["object_reference"].get_object(index)

        return self.create_day(
            start=start,
            end=end,
            path=path,
            map_=map_,
            length=length,
            min_shape=min_shape,
            max_shape=max_shape,
            sample_rate=sample_rate,
            id_=id_,
        )


    def insert_entry_start(
        self,
        path: str,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        length: int = 0,
        min_shape: tuple[int] = (),
        max_shape: tuple[int] = (),
        sample_rate: float | str | Decimal | None = None,
        file_id: str | uuid.UUID | None = None,
        day_path: str | None = None,
        day_id: str | uuid.UUID | None = None,
    ) -> None:
        index, day_start = self.find_day_start(start, approx=True, tails=True, sentinel=(0, None))

        if day_start is not None and date.fromtimestamp(day_start.timestamp()) == date.fromtimestamp(start.timestamp()):
            day = self.days_dataset.components["object_reference"].get_object(index)
        else:
            day = self.create_day(
                start=start,
                end=end,
                length=length,
                min_shape=min_shape,
                max_shape=max_shape,
                sample_rate=sample_rate,
                path=day_path,
                id_=day_id,
            )

        day.components["leaf_content"].insert_entry_start(
            path=path,
            length=length,
            start=start,
            end=end,
            min_shape=min_shape,
            max_shape=max_shape,
            sample_rate=sample_rate,
            id_=file_id,
        )
        day_length = day.get_field("Length").sum()
        true_day_start = day.components["start_times"].start_nanostamp
        true_day_end = day.components["end_times"].end_nanostamp
        self.days_dataset.components["node_content"].set_entry(
            index=index,
            start=true_day_start,
            end=true_day_end,
            length=day_length,
            min_shape=min_shape,
            max_shape=max_shape,
            sample_rate=sample_rate,
        )



