""" xltekvideodatasetcomponent.py
A node component which implements xltek video information in its dataset.
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
from datetime import datetime
from decimal import Decimal
from typing import Any
import uuid

# Third-Party Packages #
from dspobjects.time import nanostamp
from hdf5objects import HDF5Map, HDF5Dataset
from hdf5objects.treehierarchy import NodeDatasetComponent
import numpy as np

# Local Packages #


# Definitions #
# Classes #
class XLTEKVideoDatsetComponent(NodeDatasetComponent):
    """A node component which implements xltek video information in its dataset.

    Class Attributes:
        default_i_axis: The default dimension which the ID axis is on.
        defaulte_id_name: The default name of the ID axis.
        default_i_axis: The default dimension which the ID axis is on.
        defaulte_id_name: The default name of the ID axis.

    Attributes:
        i_axis: The dimension which the ID axis is on.
        id_name: The name of the ID axis.
        _id_axis: The ID axis of the dataset
        s_axis: The dimension which the start axis is on.
        start_name: The name of the start axis.
        _start_axis: The start time axis of the dataset
        e_axis: The dimension which the end axis is on.
        end_name: The name of the end axis.
        _end_axis: The end time axis of the dataset

    Args:
        composite: The object which this object is a component of.
        i_axis: The dimension which the ID axis is on.
        id_name: The name of the ID axis.
        s_axis: The dimension which the start axis is on.
        start_name: The name of the start axis.
        e_axis: The dimension which the end axis is on.
        end_name: The name of the end axis.
        **kwargs: Keyword arguments for inheritance.
    """
    default_i_axis = 0
    default_id_name = "id_axis"
    default_s_axis = 0
    default_start_name = "start_time_axis"
    default_e_axis = 0
    default_end_name = "end_time_axis"

    # Magic Methods
    # Constructors/Destructors
    def __init__(
        self,
        composite: Any = None,
        i_axis: int | None = None,
        id_name: str | None = None,
        s_axis: int | None = None,
        start_name: str | None = None,
        e_axis: int | None = None,
        end_name: str | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.i_axis: int = self.default_i_axis
        self.id_name: str = self.default_id_name
        self._id_axis: HDF5Dataset | None = None

        self.s_axis: int = self.default_s_axis
        self.start_name: str = self.default_start_name
        self._start_axis: HDF5Dataset | None = None

        self.e_axis: int = self.default_e_axis
        self.end_name: str = self.default_end_name
        self._end_axis: HDF5Dataset | None = None

        # Parent Attributes #
        super().__init__(self, init=False)

        # Object Construction #
        if init:
            self.construct(
                composite=composite,
                s_axis=s_axis,
                start_name=start_name,
                e_axis=e_axis,
                end_name=end_name,
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
        i_axis: int | None = None,
        id_name: str | None = None,
        s_axis: int | None = None,
        start_name: str | None = None,
        e_axis: int | None = None,
        end_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            composite: The object which this object is a component of.
            i_axis: The dimension which the ID axis is on.
        id_name: The name of the ID axis.
            s_axis: The dimension which the start axis is on.
            start_name: The name of the start axis.
            e_axis: The dimension which the end axis is on.
            end_name: The name of the end axis.
            **kwargs: Keyword arguments for inheritance.
        """
        if i_axis is not None:
            self.i_axis = i_axis

        if id_name is not None:
            self.id_name = id_name

        if s_axis is not None:
            self.s_axis = s_axis

        if start_name is not None:
            self.start_name = start_name

        if e_axis is not None:
            self.e_axis = e_axis

        if end_name is not None:
            self.end_name = end_name

        super().construct(composite=composite, **kwargs)

    # Node
    def set_entry(
        self,
        index: int,
        path: str | None = None,
        start: datetime | float | int | np.dtype | None = None,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int | None = None,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        """Set an entry's values based on the given parameters.

        Args:
            index: The index to set the given entry.
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            id_: The ID of the entry.
        """
        item = {}

        if path is not None:
            item["Path"] = path

        if length is not None:
            item["Length"] = length

        if sample_rate is not None:
            item["Sample Rate"] = float(sample_rate)

        self.set_entry_dict(index, item, map_)

        if id_ is not None:
            self.id_axis.components["axis"].insert_id(id_, index=index)

        if start is not None:
            self.start_axis.set_item(index, nanostamp(start))

        if end is not None:
            self.end_axis.set_item(index, nanostamp(end))

    def append_entry(
        self,
        path: str,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        """Append an entry to dataset.

        Args:
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            id_: The ID of the entry.
        """
        self.append_entry_dict(
            item={
                "Path": path,
                "Length": length,
                "Sample Rate": float(sample_rate) if sample_rate is not None else np.nan,
            },
            map_=map_,
        )
        self.id_axis.components["axis"].append_id(id_ if id_ is not None else uuid.uuid4())
        self.start_axis.append_data(nanostamp(start))
        self.end_axis.append_data(nanostamp(end if end is not None else start))

    def insert_entry(
        self,
        index: int,
        path: str,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        """Insert an entry into dataset.

        Args:
            index: The index to insert the given entry.
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            id_: The ID of the entry.
        """
        self.insert_entry_dict(
            index=index,
            item={
                "Path": path,
                "Length": length,
                "Sample Rate": float(sample_rate) if sample_rate is not None else np.nan,
            },
            map_=map_,
        )
        self.id_axis.components["axis"].append_id(id_ if id_ is not None else uuid.uuid4())
        self.start_axis.append_data(nanostamp(start))
        self.end_axis.append_data(nanostamp(end if end is not None else start))

    def insert_entry_start(
        self,
        path: str,
        map_: HDF5Map,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        length: int = 0,
        id_: str | uuid.UUID | None = None,
    ) -> None:
        """Inserts an entry into dataset based on the start time.

        Args:
            path: The path name which the entry represents.
            map_: The map to the object that should be stored in the entry.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            length: The number of samples in the entry.
            id_: The ID of the entry.
        """
        if self.composite.size == 0:
            self.append_node_entry(
                path=path,
                map_=map_,
                start=start,
                end=end,
                length=length,
                sample_rate=sample_rate,
                id_=id_,
            )
        else:
            index, dt = self.start_axis.components["axis"].find_time_index(start, approx=True, tails=True)

            if dt != start:
                self.insert_entry(
                    index=index,
                    path=path,
                    map_=map_,
                    start=start,
                    end=end,
                    length=length,
                    sample_rate=sample_rate,
                    id_=id_,
                )
            else:
                raise ValueError("Entry already exists")

    def update_entry(self, index: int) -> None:
        """Updates an entry to the correct information of the child.

        Args:
            index: The index of the entry to update.
        """
        child = self.composite.file[self.composite.dtypes_dict[self.reference_field]]
        self.set_entry(
            index=index,
            start=child.get_start_datetime(),
            end=child.get_end_datetime(),
            length=child.length,
            sample_rate=child.sample_rate,
        )

    def update_entries(self) -> None:
        """Updates all entries to the correct information of their child."""
        child_refs = self.composite.get_field(reference_field)
        data = self.composite[...]
        starts = self.start_axis[...]
        ends = self.end_axis[...]
        for i, child_ref in enumerate(child_refs):
            child = self.composite.file[child_ref]
            new = {
                "Length": child.length,
                "Sample Rate": child.sample_rate,
            }
            data[i] = self.composite.item_to_dict(self.composite.item_to_dict(data[i]) | new)
            starts[i] = nanostamp(child.get_start_datetime())
            ends[i] = nanostamp(child.get_end_datetime())

        self.composite.data_exclusively(data)
        self.start_axis.data_exclusively(starts)
        self.start_axis.data_exclusively(ends)
