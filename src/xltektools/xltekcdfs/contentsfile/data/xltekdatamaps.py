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
from cdfs.contentsfile import TimeContentGroupComponent
from cdfs.contentsfile import TimeContentGroupMap


# Local Packages #


# Definitions #
# Classes #
class XLTEKDataDayGroupMap(TimeContentGroupMap):
    """A group map which outlines a group with basic node methods."""

    default_attributes = {"tree_type": "Leaf"}
    default_component_types = {
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
    default_component_types = {
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
