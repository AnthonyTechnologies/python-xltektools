""" xltekvideomaps.py

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

# Third-Party Packages #
import h5py
from hdf5objects.dataset import TimeAxisMap, IDAxisMap
from hdf5objects.dataset import ObjectReferenceComponent, TimeSeriesComponent
from hdf5objects.treehierarchy import BaseNodeDatasetMap, BaseNodeGroupMap
import numpy as np

# Local Packages #
from cdfs.contentsfile import TimeContentDatasetComponent, TimeContentGroupMap, TimeContentGroupComponent

# Local Packages #
from .xltekvideodatasetcomponent import XLTEKVideoDatsetComponent
from .xltekvideogroupcomponent import XLTEKVideoGroupComponent


# Definitions #
# Classes #
class XLTEKVideoDatasetMap(BaseNodeDatasetMap):
    """A map for a dataset that outlines timed data across multiple files."""
    default_attribute_names = {"t_axis": "t_axis"}
    default_attributes = {"t_axis": 0}
    default_dtype = (
        ("Node", h5py.ref_dtype),
        ("Path", str),
        ("Length", np.uint64),
        ("Sample Rate", np.float64),
    )
    default_axis_maps = [{
        "id_axis": IDAxisMap(component_kwargs = {"axis": {"is_uuid": True}}),
        "start_time_axis": TimeAxisMap(),
        "end_time_axis": TimeAxisMap(),
    }]
    default_component_types = {
        "object_reference": (ObjectReferenceComponent, {"reference_fields": {"node": "Node"},
                                                        "primary_reference_field": "node",
                                                        }
                             ),
        "start_times": (TimeSeriesComponent, {"scale_name": "start_time_axis"}),
        "end_times": (TimeSeriesComponent, {"scale_name": "end_time_axis"}),
        "tree_node": (XLTEKVideoDatsetComponent, {}),
    }
    default_kwargs = {"shape": (0,), "maxshape": (None,)}


class BaseXLTEKVideoGroupMap(BaseNodeGroupMap):
    """A group map which outlines a group with basic node methods."""
    default_attribute_names = {"tree_type": "tree_type"}
    default_attributes = {"tree_type": "Node"}
    default_map_names = {"node_map": "node_map"}
    default_maps = {"node_map": XLTEKVideoDatasetMap()}
    default_component_types = {
        "tree_node": (XLTEKVideoGroupComponent, {}),
    }


class XLTEKVideoDayGroupMap(BaseXLTEKVideoGroupMap):
    """A group map which outlines a group with basic node methods."""
    default_attributes = {"tree_type": "Leaf"}
    default_component_types = {
        "tree_node": (XLTEKVideoGroupComponent, {"insert_name": "insert_recursive_entry_start"}),
    }


class XLTEKVideoContentGroupMap(BaseXLTEKVideoGroupMap):
    """A group map which outlines a group with basic node methods."""
    default_attributes = {"tree_type": "Node"}
    default_component_types = {
        "tree_node": (XLTEKVideoGroupComponent, {"insert_name": "insert_recursive_entry_start_date",
                                                 "child_map_type": XLTEKVideoDayGroupMap
                                                 }),
    }
