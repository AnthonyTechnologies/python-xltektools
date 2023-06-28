""" contentdatasetcomponent.py
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
from datetime import datetime
from decimal import Decimal
from typing import Any
import uuid

# Third-Party Packages #
from cdfs.contentsfile import TimeContentDatasetComponent
from dspobjects.time import nanostamp
from hdf5objects import HDF5Map, HDF5Dataset
import numpy as np

# Local Packages #


# Definitions #
# Classes #
class XLTEKContentDatasetComponent(TimeContentDatasetComponent):
    """A node component which implements xltek content information in its dataset."""

    # Instance Methods #
    def set_entry(
        self,
        index: int,
        path: str | None = None,
        start: datetime | float | int | np.dtype | None = None,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        axis: int | None = None,
        min_shape: tuple[int] | None = None,
        max_shape: tuple[int] | None = None,
        id_: str | uuid.UUID | None = None,
        start_id: int | None = None,
        end_id: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Set an entry's values based on the given parameters.

        Args:
            index: The index to set the given entry.
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            axis: The axis dimension number which the data concatenated along.
            min_shape: The minimum shape in the entry.
            max_shape: The maximum shape in the entry.
            id_: The ID of the entry.
        """
        item = {}

        if path is not None:
            item["Path"] = path

        if axis is not None:
            item["Axis"] = axis

        if sample_rate is not None:
            item["Sample Rate"] = float(sample_rate)

        if start_id is not None:
            item["Start ID"] = axis

        if end_id is not None:
            item["End ID"] = axis

        self.set_entry_dict(index, item, map_)

        if min_shape is not None:
            mins_shape = self.region_references.get_object(index=index, ref_name=self.mins_name).components["shapes"]
            mins_shape.set_shape(index=index, shape=min_shape)

        if max_shape is not None:
            maxs_shape = self.region_references.get_object(index=index, ref_name=self.maxs_name).components["shapes"]
            maxs_shape.set_shape(index=index, shape=max_shape)

        if id_ is not None:
            self.id_axis.components["axis"].insert_id(id_, index=index)

        if start is not None:
            self.start_axis[index] = nanostamp(start)

        if end is not None:
            self.end_axis[index] = nanostamp(end)

    def append_entry(
        self,
        path: str,
        start: datetime | float | int | np.dtype,
        end: datetime | float | int | np.dtype | None = None,
        sample_rate: float | str | Decimal | None = None,
        map_: HDF5Map | None = None,
        axis: int = 0,
        min_shape: tuple[int] = (0,),
        max_shape: tuple[int] = (0,),
        id_: str | uuid.UUID | None = None,
        start_id: int = 0,
        end_id: int = 0,
        **kwargs: Any,
    ) -> None:
        """Append an entry to dataset.

        Args:
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            axis: The axis dimension number which the data concatiated along.
            min_shape: The minimum shape in the entry.
            max_shape: The maximum shape in the entry.
            id_: The ID of the entry.
        """
        self.min_shapes.append_data(np.array(min_shape))
        _, min_ref = self.region_references.generate_region_reference(
            (-1, slice(None)),
            ref_name=self.mins_name,
        )
        self.max_shapes.append_data(np.array(max_shape))
        _, max_ref = self.region_references.generate_region_reference(
            (-1, slice(None)),
            ref_name=self.maxs_name,
        )

        self.append_entry_dict(
            item={
                "Path": path,
                "Axis": axis,
                "Minimum Shape": min_ref,
                "Maximum Shape": max_ref,
                "Sample Rate": float(sample_rate) if sample_rate is not None else np.nan,
                "Start ID": start_id,
                "End ID": end_id,
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
        axis: int = 0,
        min_shape: tuple[int] = (0,),
        max_shape: tuple[int] = (0,),
        id_: str | uuid.UUID | None = None,
        start_id: int = 0,
        end_id: int = 0,
        **kwargs: Any,
    ) -> None:
        """Insert an entry into dataset.

        Args:
            index: The index to insert the given entry.
            path: The path name which the entry represents.
            start: The start time of the entry.
            end: The end time of the entry.
            sample_rate: The sample rate of the entry.
            map_: The map to the object that should be stored in the entry.
            axis: The axis dimension number which the data concatenated along.
            min_shape: The minimum shape in the entry.
            max_shape: The maximum shape in the entry.
            id_: The ID of the entry.
        """
        if self.composite.size == 0 or index == len(self.composite):
            self.append_entry(
                path=path,
                map_=map_,
                start=start,
                end=end,
                axis=axis,
                min_shape=min_shape,
                max_shape=max_shape,
                sample_rate=sample_rate,
                id_=id_,
                start_id=start_id,
                end_id=end_id,
                **kwargs,
            )
        else:
            self.min_shapes.insert_data(index, np.array(min_shape))
            min_object, min_ref = self.region_references.generate_region_reference(
                (index, slice(None)),
                ref_name=self.mins_name,
            )
            self.max_shapes.insert_data(index, np.array(max_shape))
            max_object, max_ref = self.region_references.generate_region_reference(
                (index, slice(None)),
                ref_name=self.maxs_name,
            )

            self.insert_entry_dict(
                index=index,
                item={
                    "Path": path,
                    "Axis": axis,
                    "Minimum Shape": min_ref,
                    "Maximum Shape": max_ref,
                    "Sample Rate": float(sample_rate) if sample_rate is not None else np.nan,
                    "Start ID": start_id,
                    "End ID": end_id,
                },
                map_=map_,
            )
            self.fix_shape_references()
            self.id_axis.components["axis"].insert_id(index=index, id_=id_ if id_ is not None else uuid.uuid4())
            self.start_axis.insert_data(index, nanostamp(start))
            self.end_axis.insert_data(index, nanostamp(end if end is not None else start))
