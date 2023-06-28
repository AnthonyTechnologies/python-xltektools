"""xltekdatamaps.py

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
from cdfs.contentsfile import TimeContentGroupComponent, TimeContentDatasetMap, TimeContentGroupMap
import numpy as np

# Local Packages #
from .xltekcontentdatasetcomponent import XLTEKContentDatasetComponent


# Definitions #
# Classes #
class XLTEKContentDatasetMap(TimeContentDatasetMap):
    """A map for a dataset that outlines timed data across multiple files."""

    default_dtype = TimeContentDatasetMap.default_dtype + (("Start ID", np.int64), ("End ID", np.int64))
    default_component_types = TimeContentDatasetMap.default_component_types | {
        "tree_node": (XLTEKContentDatasetComponent, {}),
    }


class XLTEKContentGroupMap(TimeContentGroupMap):
    """A group map which outlines a group with basic node methods."""

    default_attributes = {"tree_type": "Node"}
    default_maps = TimeContentGroupMap.default_maps | {
        "node_map": XLTEKContentDatasetMap(),
    }


class XLTEKDataDayGroupMap(XLTEKContentGroupMap):
    """A group map which outlines a group with basic node methods."""

    default_attributes = {"tree_type": "Leaf"}
    default_component_types = XLTEKContentGroupMap.default_component_types | {
        "tree_node": (
            TimeContentGroupComponent,
            {
                "set_method": "set_recursive_entry_start",
                "append_method": "append_recursive_entry_start",
                "insert_method": "insert_recursive_entry_start",
            },
        ),
    }


class XLTEKDataContentGroupMap(TimeContentGroupMap):
    """A group map which outlines a group with basic node methods."""

    default_attributes = {"tree_type": "Node"}
    default_component_types = TimeContentGroupMap.default_component_types | {
        "tree_node": (
            TimeContentGroupComponent,
            {
                "set_method": "set_recursive_entry_start_date",
                "append_method": "append_recursive_entry_start_date",
                "insert_method": "insert_recursive_entry_start_date",
                "child_map_type": XLTEKDataDayGroupMap,
            },
        ),
    }
