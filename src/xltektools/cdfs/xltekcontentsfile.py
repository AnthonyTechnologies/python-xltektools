""" xltekcontentsfile.py

"""
# Package Header #
from ..header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from collections.abc import Mapping

# Third-Party Packages #
from hdf5objects import HDF5Map
from cdfs.contentsfile import TimeContentsFileMap, TimeContentsFile, TimeNodeMap, TimeLeafMap

# Local Packages #
from .xltekdatagroupcomponent import XLTEKDataGroupComponent


# Definitions #
# Classes #
class XLETKDataContentMap(HDF5Map):
    default_map_names: Mapping[str, str] = {"days": "days"}
    default_maps: Mapping[str, HDF5Map] = {
        "days": TimeNodeMap(shape=(0,), maxshape=(None,)),
    }
    default_component_types = {"xltek_data": (XLTEKDataGroupComponent, {"day_map_type": TimeLeafMap})}


class XLTEKContentsFileMap(TimeContentsFileMap):
    """A map for BaseHDF5 files."""
    default_maps: Mapping[str, HDF5Map] = {
        "data_content": XLETKDataContentMap(),
    }


class XLTEKContentsFile(TimeContentsFile):
    FILE_TYPE: str = "ContentsFile"
    default_map: HDF5Map = XLTEKContentsFileMap()
