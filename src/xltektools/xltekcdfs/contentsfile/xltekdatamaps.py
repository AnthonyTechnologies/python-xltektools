""" xltekdatamaps.py

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

# Third-Party Packages #
from cdfs.contentsfile import TimeContentGroupMap, TimeContentGroupComponent

# Local Packages #


# Definitions #
# Classes #
class XLTEKDataDayGroupMap(TimeContentGroupMap):
    """A group map which outlines a group with basic node methods."""
    default_attributes = {"tree_type": "Leaf"}
    default_component_types = {
        "tree_node": (TimeContentGroupComponent, {"insert_name": "insert_recursive_entry_start"}),
    }


class XLTEKDataContentGroupMap(TimeContentGroupMap):
    """A group map which outlines a group with basic node methods."""
    default_attributes = {"tree_type": "Node"}
    default_component_types = {
        "tree_node": (TimeContentGroupComponent, {"insert_name": "insert_recursive_entry_start_date",
                                                  "child_map_type": XLTEKDataDayGroupMap
                                                  }),
    }
