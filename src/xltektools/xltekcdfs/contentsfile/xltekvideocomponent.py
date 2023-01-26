""" xltekvideocomponent.py

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
from datetime import datetime
import uuid

# Third-Party Packages #
from dspobjects.time import nanostamp
from hdf5objects import HDF5Dataset
from hdf5objects.dataset import BaseDatasetComponent
import numpy as np

# Local Packages #


# Definitions #
# Classes #
class XLTEKVideoComponent(BaseDatasetComponent):
    # Magic Methods
    # Constructors/Destructors
    def __init__(
        self,
        composite: Any = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.i_axis: int = 0
        self.id_name: str = "id_axis"
        self._id_axis = None

        self.s_axis: int = 0
        self.start_name: str = "start_time_axis"
        self._start_axis = None

        self.e_axis: int = 0
        self.end_name: str = "end_time_axis"
        self._end_axis = None

        # Parent Attributes #
        super().__init__(self, init=False)

        # Object Construction #
        if init:
            self.construct(
                composite=composite,
                **kwargs,
            )

    @property
    def id_axis(self) -> HDF5Dataset | None:
        """Loads and returns the id axis."""
        if self._id_axis is None:
            self._id_axis = self.composite.axes[self.i_axis][self.id_name]
        return self._id_axis

    @id_axis.setter
    def id_axis(self, value: HDF5Dataset | None) -> None:
        self._id_axis = value

    @property
    def start_axis(self) -> HDF5Dataset | None:
        """Loads and returns the start time axis."""
        if self._start_axis is None:
            self._start_axis = self.composite.axes[self.s_axis][self.start_name]
        return self._start_axis

    @start_axis.setter
    def start_axis(self, value: HDF5Dataset | None) -> None:
        self._start_axis = value

    @property
    def end_axis(self) -> HDF5Dataset | None:
        """Loads and returns the end time axis."""
        if self._end_axis is None:
            self._end_axis = self.composite.axes[self.e_axis][self.end_name]
        return self._end_axis

    @end_axis.setter
    def end_axis(self, value: HDF5Dataset | None) -> None:
        self._end_axis = value

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        composite: Any = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            composite: The object which this object is a component of.
            **kwargs: Keyword arguments for inheritance.
        """
        super().construct(composite=composite, **kwargs)

    # InstanceMethods #
    # Constructors/Destructors
    def set_entry(
        self,
        index: int,
        path: str | None = None,
        start: datetime | float | int | np.dtype | None = None,
        end: datetime | float | int | np.dtype | None = None,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        """Set an entry's values based on the given parameters.

        Args:
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            id_: The ID of the entry.
        """
        item = {}

        if path is not None:
            item["Path"] = path

        self.composite.set_item_dict(index, item)

        if id_ is not None:
            self.id_axis.components["axis"].insert_id(id_ if id_ is not None else uuid.uuid4(), index=index)

        if start is not None:
            self.start_axis.set_item(index, start)

        if end is not None:
            self.end_axis.set_item(index, end)

    def append_entry(
        self,
        path: str,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        """Append an entry to dataset.

        Args:
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            id_: The ID of the entry.
        """
        self.composite.append_data_item_dict({
            "Path": path,
        })
        self.id_axis.components["axis"].append_id(id_ if id_ is not None else uuid.uuid4())
        self.start_axis.append_data(nanostamp(start))
        self.end_axis.append_data(nanostamp(end if end is not None else start))

    def insert_entry_start(
        self,
        path: str,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        """Inserts an entry into dataset based on the start time.

        Args:
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            id_: The ID of the entry.
        """
        if self.composite.size == 0:
            self.append_entry(
                path=path,
                start=start,
                end=end,
                id_=id_,
            )
        else:
            index, dt = self.start_axis.components["axis"].find_time_index(start, approx=True, tails=True)

            if dt != start:
                self.composite.insert_data_item_dict(
                    {"Path": path},
                    index=index,
                )
                self.id_axis.components["axis"].insert_id(id_ if id_ is not None else uuid.uuid4(), index=index)
                self.start_axis.insert_data(nanostamp(start), index=index)
                self.end_axis.insert_data(nanostamp(end if end is not None else start), index=index)
            else:
                raise ValueError("Entry already exists")
