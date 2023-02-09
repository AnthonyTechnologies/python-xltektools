""" xltekvideogroupcomponent.py
A node component which implements an interface for a time content dataset.
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
from collections.abc import Iterable, Iterator
from datetime import datetime, date, tzinfo
from decimal import Decimal
from typing import Any
import uuid

# Third-Party Packages #
from baseobjects.typing import AnyCallable
from dspobjects.time import Timestamp, nanostamp
from hdf5objects import HDF5Map, HDF5Dataset
from hdf5objects.treehierarchy import NodeGroupComponent
import numpy as np

# Local Packages #



# Definitions #
# Classes #
class XLTEKVideoGroupComponent(NodeGroupComponent):
    """A node component which implements an interface for a content dataset.

       Attributes:
           _insert_recursive_entry: The method to use as the insert recursive entry method.

       Args:
           composite: The object which this object is a component of.
           insert_name: The attribute name of the method to use as the insert recursive entry method.
           init: Determines if this object will construct.
           **kwargs: Keyword arguments for inheritance.
       """

    # Magic Methods #
    # Constructors/Destructors
    def __init__(
        self,
        composite: Any = None,
        insert_name: str | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self._insert_recursive_entry: AnyCallable = self.insert_recursive_entry_default.__func__

        # Parent Attributes #
        super().__init__(self, init=False)

        # Object Construction #
        if init:
            self.construct(
                composite=composite,
                insert_name=insert_name,
                **kwargs,
            )

    @property
    def length(self) -> int:
        """The minimum shape of this node."""
        return self.map_dataset.get_field("Length").sum()

    @property
    def sample_rate(self) -> float:
        """The sample rate of this node if all children have the same sample_rate."""
        sample_rates = self.map_dataset.get_field("Sample Rate")
        min_sample_rate = sample_rates.min()
        return min_sample_rate if (sample_rates == min_sample_rate).all() else np.nan

    @property
    def insert_recursive_entry(self) -> AnyCallable:
        """A descriptor to create the bound insert recursive entry method."""
        return self._insert_recursive_entry.__get__(self, self.__class__)

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        composite: Any = None,
        insert_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            composite: The object which this object is a component of.
            insert_name: The attribute name of the method to use as the insert recursive entry method.
            **kwargs: Keyword arguments for inheritance.
        """
        if insert_name is not None:
            self.set_insert_recursive_entry_method(insert_name)

        super().construct(composite=composite, **kwargs)

    def set_insert_recursive_entry_method(self, name: str) -> None:
        """Sets insert recursive entry method to a method within this object.

        Args:
            The attribute name of the method to use as the insert recursive entry method.
        """
        self._insert_recursive_entry = getattr(self, name).__func__

    def get_start_datetime(self):
        """Gets the start datetime of this node.

        Returns:
            The start datetime of this node.
        """
        return self.map_dataset.components["start_times"].start_datetime if self.map_dataset.size != 0 else None

    def get_end_datetime(self):
        """Gets the end datetime of this node.

        Returns:
            The end datetime of this node.
        """
        return self.map_dataset.components["end_times"].end_datetime if self.map_dataset.size != 0 else None

    def set_time_zone(self, value: str | tzinfo | None = None, offset: float | None = None) -> None:
        """Sets the timezone of the start and end time axes.

        Args:
            value: The time zone to set this axis to.
            offset: The time zone offset from UTC.
        """
        self.map_dataset.components["start_times"].set_tzinfo(value)
        self.map_dataset.components["end_times"].set_tzinfo(value)
        if self.map_dataset.size != 0:
            for group in self.map_dataset.components["object_reference"].get_objects_iter():
                group.components["contents_node"].set_time_zone(value)

    def find_child_index_start(
        self,
        start: datetime | float | int | np.dtype,
        approx: bool = True,
        tails: bool = True,
        sentinel: Any = (None, None),
    ) -> tuple[int, datetime]:
        """Finds the index of a child in the dataset using the start.

        Args:
            start: The start of the child to find.
            approx: Determines if the closest child to the given start will be returned or if it must be exact.
            tails: Determines if the closest child will be returned if the given start is outside the minimum and
                   maximum starts of the children.

        Returns:
            The index of in the child and the datetime at that index.
        """
        if self.map_dataset.size != 0:
            return self.map_dataset.components["start_times"].find_time_index(start, approx=approx, tails=tails)
        else:
            return sentinel

    def find_child_index_start_date(
        self,
        start: datetime | date | float | int | np.dtype,
        approx: bool = True,
        tails: bool = True,
        sentinel: Any = (None, None),
    ) -> tuple[int, datetime]:
        """Finds the index of a child in the dataset using the start.

        Args:
            start: The start of the child to find.
            approx: Determines if the closest child to the given start will be returned or if it must be exact.
            tails: Determines if the closest child will be returned if the given start is outside the minimum and
                   maximum starts of the children.

        Returns:
            The index of in the child and the datetime at that index.
        """
        tz = None
        if isinstance(start, datetime):
            tz = start.tzinfo
            start = start.date()
        if not isinstance(start, date):
            start = Timestamp(nanostamp(start)).date()

        start = Timestamp(start, tz=tz)

        if self.map_dataset.size != 0:
            return self.map_dataset.components["start_times"].find_time_index(start, approx=approx, tails=tails)
        else:
            return sentinel

    def create_child(
        self,
        index: int,
        path: str,
        start: datetime | date | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        id_: str | uuid.UUID | None = None,
    ) -> HDF5Dataset | None:
        """Creates a child node and inserts it as an entry.

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
        if map_ is None and self.child_map_type is not None:
            map_ = self.child_map_type(name=f"{self.composite.name}/{path}")
            self.composite.map.set_item(map_)

        self.map_dataset.components[self.node_component_name].insert_entry(
            index=index,
            path=path,
            start=start,
            end=end,
            sample_rate=sample_rate,
            map_=map_,
            length=length,
            id_=id_,
        )

        if map_ is None:
            return None
        else:
            start_tz = self.map_dataset.components["start_times"].time_axis.time_zone
            end_tz = self.map_dataset.components["end_times"].time_axis.time_zone

            child = map_.get_object(require=True, file=self.composite.file)
            if start_tz is not None:
                child.components[self.child_component_name].map_dataset.components["start_times"].set_tzinfo(start_tz)

            if end_tz is not None:
                child.components[self.child_component_name].map_dataset.components["end_times"].set_tzinfo(end_tz)

            return child

    def require_child_start(
        self,
        path: str,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        id_: str | uuid.UUID | None = None,
    ) -> tuple[int, HDF5Dataset]:
        """Gets a child node matching the start datetime or if does not exist, creates and inserts it as an entry.

        Args:
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            id_: The ID of the entry.
        """
        start = nanostamp(start)

        if self.map_dataset.size != 0:
            index, dt = self.map_dataset.components["start_times"].find_time_index(start, approx=True, tails=True)

            if nanostamp(dt) == start:
                if self.child_map_type is not None:
                    return index, self.map_dataset.components["object_reference"].get_object(index, ref_name="node")
                else:
                    return index, None
        else:
            index = 0

        return index, self.create_child(
            index=index,
            path=path,
            start=start,
            end=end,
            sample_rate=sample_rate,
            map_=map_,
            length=length,
            id_=id_,
        )

    def require_child_start_date(
        self,
        path: str,
        start: datetime | date | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        id_: str | uuid.UUID | None = None,
    ) -> tuple[int, HDF5Dataset]:
        """Gets a child node matching the start date or if does not exist, creates and inserts it as an entry.

        Args:
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            min_shape: The minimum shape in the entry.
            max_shape: The maximum shape in the entry.
            id_: The ID of the entry.
        """
        tz = None
        if isinstance(start, datetime):
            tz = start.tzinfo
            start_date = start.date()
        elif isinstance(start, date):
            start_date = start
        else:
            start_date = Timestamp(nanostamp(start)).date()

        start_date = Timestamp(start_date, tz=tz)

        if self.map_dataset.size != 0:
            index, dt = self.map_dataset.components["start_times"].find_time_index(start_date, approx=True, tails=True)

            if dt.date() == start_date.date():
                if self.child_map_type is not None:
                    return index, self.map_dataset.components["object_reference"].get_object(index, ref_name="node")
                else:
                    return index, None
        else:
            index = 0

        return index, self.create_child(
            index=index,
            path=path,
            start=start,
            end=end,
            sample_rate=sample_rate,
            map_=map_,
            length=length,
            id_=id_,
        )

    def insert_recursive_entry_default(
        self,
        indicies: Iterable[int],
        paths: Iterable[str],
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        ids: Iterable[str | uuid.UUID | None] | None = None,
    ) -> None:
        """Inserts an entry recursively into its children using indicies.

        Args:
            indicies: The indicies to recursively insert into.
            paths: The path names which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            ids: The child IDs for the entry.
        """
        if not isinstance(indicies, list):
            indicies = list(indicies)

        if not isinstance(paths, list):
            paths = list(paths)

        if ids is not None and not isinstance(ids, list):
            ids = list(ids)

        index = indicies.pop(0)
        path = paths.pop(0)
        id_ = ids.pop(0) if ids else None
        child = self.create_child(
            index=index,
            path=path,
            start=start,
            end=end,
            sample_rate=sample_rate,
            map_=map_,
            length=length,
            id_=id_,
        )
        if paths:
            child.components[self.child_component_name].insert_recursive_entry(
                paths=paths,
                start=start,
                end=end,
                sample_rate=sample_rate,
                map_=map_,
                length=length,
                ids=ids,
            )

            self.map_dataset.components[self.node_component_name].set_entry(
                index=index,
                start=child.get_start_datetime(),
                end=child.get_end_datetime(),
                length=child.length,
                sample_rate=child.sample_rate,
            )

    def insert_recursive_entry_start(
        self,
        paths: Iterable[str],
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        ids: Iterable[str | uuid.UUID | None] | None = None,
    ) -> None:
        """Inserts an entry recursively into its children using the start datetime.

        Args:
            paths: The path names which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            ids: The child IDs for the entry.
        """
        if not isinstance(paths, list):
            paths = list(paths)

        if ids is not None and not isinstance(ids, list):
            ids = list(ids)

        path = paths.pop(0)
        id_ = ids.pop(0) if ids else None
        index, child = self.require_child_start(
            path=path,
            start=start,
            end=end,
            sample_rate=sample_rate,
            map_=map_,
            length=length,
            id_=id_,
        )
        if paths:
            child_node_component = child.components[self.child_component_name]
            child_node_component.insert_recursive_entry(
                paths=paths,
                start=start,
                end=end,
                sample_rate=sample_rate,
                map_=map_,
                length=length,
                ids=ids,
            )

            self.map_dataset.components[self.node_component_name].set_entry(
                index=index,
                start=child_node_component.get_start_datetime(),
                end=child_node_component.get_end_datetime(),
                sample_rate=child_node_component.sample_rate,
                length=child_node_component.length,
            )

    def insert_recursive_entry_start_date(
        self,
        paths: Iterable[str],
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        length: int = 0,
        ids: Iterable[str | uuid.UUID | None] | None = None,
    ) -> None:
        """Inserts an entry recursively into its children using the start date.

        Args:
            paths: The path names which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            length: The number of samples in the entry.
            ids: The child IDs for the entry.
        """
        if not isinstance(paths, list):
            paths = list(paths)

        if ids is not None and not isinstance(ids, list):
            ids = list(ids)

        path = paths.pop(0)
        id_ = ids.pop(0) if ids else None
        index, child = self.require_child_start_date(
            path=path,
            start=start,
            end=end,
            sample_rate=sample_rate,
            map_=map_,
            length=length,
            id_=id_,
        )
        if paths:
            child_node_component = child.components[self.child_component_name]
            child_node_component.insert_recursive_entry(
                paths=paths,
                start=start,
                end=end,
                sample_rate=sample_rate,
                map_=map_,
                length=length,
                ids=ids,
            )

            self.map_dataset.components[self.node_component_name].set_entry(
                index=index,
                start=child_node_component.get_start_datetime(),
                end=child_node_component.get_end_datetime(),
                sample_rate=child_node_component.sample_rate,
                length=child_node_component.length,
            )
